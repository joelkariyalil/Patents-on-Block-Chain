

import os
import json
import hashlib
from datetime import datetime

import pdfplumber
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
#import openai

# ---------------------------------------
# Configuration
# ---------------------------------------

PATENT_FOLDER = "patents"
SIMILARITY_THRESHOLD = 0.8  # Set your uniqueness threshold here (L2 distance)

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

def assess_novelty(test_text, match_text):
    prompt = f"""
You are a patent examiner.

Test Document: {test_text[:1000]}

Known Prior Art: {match_text[:1000]}

Is the test document:
(a) Clearly novel
(b) An obvious modification
(c) Possibly plagiarized

Explain your reasoning.
"""

    result = llm(prompt, max_new_tokens=300)[0]["generated_text"]
    return result.strip()

# ---------------------------------------
# Step 5: Token Generation
# ---------------------------------------

def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ---------------------------------------
# Step 6: Format JSON Output
# ---------------------------------------

def create_result_json(test_text, matches, llm_judgment):
    best_match = matches[0]
    return {
        "document_id": generate_token(test_text)[:16],
        "uniqueness_score": best_match["score"],
        "is_unique": best_match["score"] > SIMILARITY_THRESHOLD,
        "matched_patent": {
            "filename": best_match["filename"],
            "similarity_score": best_match["score"]
        },
        "agent_judgment": llm_judgment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "token": generate_token(test_text)
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
    test_doc = extract_text_from_pdf("Test.pdf")

    matches = find_similar_docs(test_doc, index, patents)

    print(f"Top match: {matches[0]['filename']} with score {matches[0]['score']:.4f}")
    
    print("Asking LLM to assess novelty...")
    llm_judgment = assess_novelty(test_doc, matches[0]["text"])

    print("Creating JSON output...")
    result = create_result_json(test_doc, matches, llm_judgment)
    save_json_output(result)