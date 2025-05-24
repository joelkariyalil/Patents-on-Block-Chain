import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
import json
import hashlib
from datetime import datetime
import pdfplumber
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Paths
PATENT_FOLDER = "patents"
SIMILARITY_THRESHOLD = 0.85

# Models
model = SentenceTransformer("all-MiniLM-L6-v2")
llm = pipeline("text2text-generation", model="google/flan-t5-large")

# ----------------------------------------
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

def build_faiss_index(patents):
    texts = [doc["text"] for doc in patents]
    embeddings = model.encode(texts)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings

def find_similar_docs(test_text, index, patents, k=3):
    query_vec = model.encode([test_text])
    D, I = index.search(query_vec, k)
    return [{"filename": patents[i]["filename"], "text": patents[i]["text"], "score": float(D[0][j])} for j, i in enumerate(I[0])]

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

def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

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

# ✅ MAIN WRAPPER FUNCTION
def evaluate_document(file_path: str) -> dict:
    print("Loading patents...")
    patents = load_patents(PATENT_FOLDER)

    print("Building FAISS index...")
    index, _ = build_faiss_index(patents)

    print("Extracting test document...")
    test_doc = extract_text_from_pdf(file_path)

    print("Finding similar documents...")
    matches = find_similar_docs(test_doc, index, patents)

    print("LLM assessing novelty...")
    llm_judgment = assess_novelty(test_doc, matches[0]["text"])

    print("Generating final JSON result...")
    result = create_result_json(test_doc, matches, llm_judgment)

    return result
