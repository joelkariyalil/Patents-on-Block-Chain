

import os
import json
import hashlib
from datetime import datetime

import pdfplumber
import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer
#import openai

# ---------------------------------------
# Configuration
# ---------------------------------------

PATENT_FOLDER = "patents"
SIMILARITY_THRESHOLD = 0.3  # Set your uniqueness threshold here (L2 distance)

# ---------------------------------------
# Step 1: Load and extract text from PDF
# ---------------------------------------

def extract_text_from_pdf(filepath):
    with pdfplumber.open(filepath) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def load_patents(folder_path):
    patents = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            text = extract_text_from_pdf(os.path.join(folder_path, file))
            patents.append({"filename": file, "text": text})
    return patents

def is_probably_a_us_patent(text):
    text_lower = text.lower()
    head = text_lower[:int(len(text_lower) * 0.15)]  # Look at first 15% only
    return "united states patent" in head or "patent no." in head or "pub. no." in head

def extract_relevant_sections(text, filename="UNKNOWN"):
    lines = [" ".join(line.strip().split()) for line in text.split("\n") if line.strip()]
    lowered = text.lower()

    # -------------------------------
    # 1. Extract Title
    # -------------------------------
    title = ""
    for line in lines:
        if re.search(r"united\s+states\s+patent", line, re.I) or re.search(r"patent\s+no\.", line, re.I):
            title = line
            break

    # -------------------------------
    # 2. Extract Abstract
    # -------------------------------
    abstract = ""
    for i, line in enumerate(lines):
        if re.match(r"(?i)^abstract$", line):
            abstract = " ".join(lines[i+1:i+10])
            break
    if not abstract and "abstract" in lowered:
        start = lowered.find("abstract")
        abstract = text[start + 8 : start + 500].strip()

    # -------------------------------
    # 3. Extract Claim 1
    # -------------------------------
    claim_1 = ""
    claim_patterns = [
        r"(?i)^1[\)\.:]?\s",               # 1. or 1) or 1:
        r"(?i)^claim\s*1[\)\.:]?\s",       # Claim 1
        r"(?i)^we claim",
        r"(?i)^what is claimed is"
    ]
    for i, line in enumerate(lines):
        if any(re.match(pat, line) for pat in claim_patterns) or "claim 1" in line.lower():
            claim_1 = " ".join(lines[i:i+5])
            break
    if not claim_1 and "what is claimed is" in lowered:
        start = lowered.find("what is claimed is")
        claim_1 = text[start:start + 400]

    # -------------------------------
    # Diagnostics
    # -------------------------------
    if not title:   
        print(f"⚠️ Warning: No title found in {filename}")
    if not abstract:
        print(f"⚠️ Warning: No abstract found in {filename}")
    if not claim_1:
        print(f"⚠️ Warning: No Claim 1 found in {filename}")

    return title.strip(), abstract.strip(), claim_1.strip()

# ---------------------------------------
# Step 2: Embedding + FAISS Index
# ---------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_faiss_index(patents):
    texts = [doc["text"] for doc in patents]
    embeddings = model.encode(texts)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings

# ---------------------------------------
# Step 3: Find Similar Documents
# ---------------------------------------

def find_similar_docs(test_text, index, patents, k=3):
    query_vec = model.encode([test_text])
    D, I = index.search(query_vec, k)
    return [{"filename": patents[i]["filename"], "text": patents[i]["text"], "score": float(D[0][j])} for j, i in enumerate(I[0])]

# ---------------------------------------
# Step 4: LLM-Based Novelty Assessment (Hugging Face)
# ---------------------------------------

from transformers import pipeline

# You can try other models like mistralai/Mistral-7B-Instruct, meta-llama/Llama-2-7b-chat-hf, etc.
llm = pipeline("text2text-generation", model="google/flan-t5-large")

MAX_INPUT_TOKENS = 1800  # safe range for 2048-token models

def truncate_text(text, max_chars=1200):
    """Truncate text to a safe number of characters for models with 2048-token limits."""
    return text[:max_chars]

def assess_novelty(test_text, match_text, similarity_score, test_filename="test", match_filename="match"):
    # Use smart extraction
    title1, abstract1, claim1 = extract_relevant_sections(test_text, test_filename)
    title2, abstract2, claim2 = extract_relevant_sections(match_text, match_filename)

    # Build optimized prompt
    prompt = f"""
You are a patent examiner comparing two patent documents.
The semantic similarity score between these documents is: {similarity_score:.2f}
A higher score indicates a high degree of textual similarity.

Please determine whether the test document appears to be:
(a) Clearly novel
(b) An obvious modification
(c) Possibly plagiarized

Use the titles, abstracts, and primary claims to support your conclusion.

Test Patent:
Title: {title1}
Abstract: {abstract1}
Claim 1: {claim1}

Known Prior Art:
Title: {title2}
Abstract: {abstract2}
Claim 1: {claim2}

Provide the most appropriate option and explain briefly.
"""

    result = llm(prompt, max_new_tokens=150)[0]["generated_text"]
    return result.strip()

# ---------------------------------------
# Step 5: Token Generation
# ---------------------------------------

def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ---------------------------------------
# Step 6: Format JSON Output
# ---------------------------------------

def create_result_json(test_text, best_match, similarity_score, uniqueness_score, llm_judgment, diagnostic_note):
    clamped_uniqueness = min(max(uniqueness_score, 0.0), 1.0)

    return {
        "document_id": generate_token(test_text)[:16],
        "uniqueness_score": clamped_uniqueness,
        "is_unique": clamped_uniqueness > SIMILARITY_THRESHOLD,
        "matched_patent": {
            "filename": best_match["filename"],
            "similarity_score": round(1.0 - clamped_uniqueness, 4)
        },
        "agent_judgment": llm_judgment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "token": generate_token(test_text),
        "diagnostic": diagnostic_note
    }


def save_json_output(result, filename="uniqueness_result.json"):
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Output saved to {filename}")
    
# ---------------------------------------
# Main Workflow
# ---------------------------------------

if __name__ == "__main__":
    print("Loading patent corpus...")
    patents = load_patents(PATENT_FOLDER)
    
    print("Building FAISS index...")
    index, _ = build_faiss_index(patents)

    print("Evaluating test document...")
    #test_doc = input("\nPaste your test document abstract or claim here:\n\n")
    test_doc = extract_text_from_pdf("unique.pdf")

    matches = find_similar_docs(test_doc, index, patents)


    print("Asking LLM to assess novelty...")
    best_match = matches[0]
    uniqueness_score = best_match["score"]
    uniqueness_score = min(max(uniqueness_score, 0.0), 1.0)  # clamp
    similarity_score = 1.0 - uniqueness_score

    print(f"Top match: {best_match['filename']} with uniqueness score (L2): {uniqueness_score:.4f} and similarity score: {similarity_score:.4f}")

    llm_judgment = assess_novelty(
        test_doc,
        best_match["text"],
        similarity_score,
        "test_doc",
        best_match["filename"]
)

    print("Creating JSON output...")
    diagnostic_note = ""
    if not is_probably_a_us_patent(test_doc):
        diagnostic_note = "⚠️ Test document may not be a valid US patent (missing 'United States Patent' header or US patent number)."
    result = create_result_json(
    test_doc, best_match, similarity_score, uniqueness_score,
    llm_judgment, diagnostic_note
    )
    save_json_output(result)