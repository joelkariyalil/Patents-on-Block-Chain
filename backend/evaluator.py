from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
import os, hashlib, json
import shutil
import faiss
import numpy as np
import pdfplumber
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import sqlite3
import re

# --- Constants and Model Initialization ---
UPLOAD_DIR = "uploaded_docs"
PATENT_DIR = "patents"
DB_FILE = "patent_scores.db"
SIMILARITY_THRESHOLD = 0.3

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PATENT_DIR, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")
llm = pipeline("text2text-generation", model="google/flan-t5-large")

# --- SQLite Initialization ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            embedding BLOB
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT,
            match_filename TEXT,
            similarity_score REAL,
            timestamp TEXT
        )""")
init_db()

# --- Utility Functions ---
def extract_text(filepath):
    with pdfplumber.open(filepath) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def extract_relevant_sections(text, filename="UNKNOWN"):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = next((line for line in lines if re.search(r"(United States Patent|Patent No\.|US\d{7,})", line, re.I)), "")
    abstract = ""
    for i, line in enumerate(lines):
        if re.match(r"(?i)^abstract$", line.strip()):
            abstract = " ".join(lines[i+1:i+5])
            break
    if not abstract:
        abstract = " ".join(lines[1:6])
    claim_1 = ""
    claim_1_patterns = [
        r"(?i)^1[\)\.:]?\s", r"(?i)^claim\s*1[\)\.:]?\s",
        r"(?i)^we claim", r"(?i)^what is claimed is"
    ]
    for i, line in enumerate(lines):
        if any(re.match(pat, line) for pat in claim_1_patterns):
            claim_1 = " ".join(lines[i:i+3])
            break
    return title.strip(), abstract.strip(), claim_1.strip()

def assess_novelty(test_text, match_text, similarity_score, test_filename="test", match_filename="match"):
    title1, abstract1, claim1 = extract_relevant_sections(test_text, test_filename)
    title2, abstract2, claim2 = extract_relevant_sections(match_text, match_filename)
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

def store_embedding(filename, embedding):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT OR REPLACE INTO patents (filename, embedding) VALUES (?, ?)", (filename, embedding.tobytes()))

def fetch_embeddings():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT filename, embedding FROM patents")
        return [(row[0], np.frombuffer(row[1], dtype=np.float32)) for row in cursor.fetchall()]

def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --- Initialize Embeddings at Startup ---
def initialize_embeddings():
    for file in os.listdir(PATENT_DIR):
        if file.endswith(".pdf"):
            file_path = os.path.join(PATENT_DIR, file)
            text = extract_text(file_path)
            vec = model.encode([text])[0].astype(np.float32)
            store_embedding(file, vec)

initialize_embeddings()

# --- MAIN FUNCTION ---
def upload_and_check(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(file_path)
    query_vec = model.encode([text])[0]
    embeddings = fetch_embeddings()
    if not embeddings:
        return JSONResponse(content={"error": "No prior patents in the database"}, status_code=400)

    vectors = np.array([e[1] for e in embeddings])
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    D, I = index.search(np.array([query_vec]), k=1)

    best_match_file, uniqueness_score = embeddings[I[0][0]][0], float(D[0][0])
    similarity_score = 1.0 - min(1.0, uniqueness_score)
    match_text = extract_text(os.path.join(PATENT_DIR, best_match_file))
    judgment = assess_novelty(text, match_text, similarity_score, "test_doc", best_match_file)

    document_id = generate_token(text)[:16]
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO scores (document_id, match_filename, similarity_score, timestamp) VALUES (?, ?, ?, ?)",
                     (document_id, best_match_file, similarity_score, datetime.utcnow().isoformat()))

    if uniqueness_score > SIMILARITY_THRESHOLD:
        os.remove(file_path)
    else:
        new_patent_path = os.path.join(PATENT_DIR, file.filename)
        shutil.move(file_path, new_patent_path)
        store_embedding(file.filename, query_vec.astype(np.float32))

    return {
        "document_id": document_id,
        "uniqueness_score": uniqueness_score,
        "is_unique": uniqueness_score > SIMILARITY_THRESHOLD,
        "matched_patent": {
            "filename": best_match_file,
            "similarity_score": similarity_score
        },
        "agent_judgment": judgment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "token": generate_token(text)
    }
