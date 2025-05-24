from fastapi import FastAPI, UploadFile, File
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

app = FastAPI()

# Constants and model initialization
UPLOAD_DIR = "uploaded_docs"         # Temporary storage for uploaded files
PATENT_DIR = "patents"                # Directory to store accepted unique patents
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PATENT_DIR, exist_ok=True)
SIMILARITY_THRESHOLD = 0.3            # Threshold for deciding novelty based on L2 distance
model = SentenceTransformer("all-MiniLM-L6-v2")   # For semantic vector generation
llm = pipeline("text2text-generation", model="google/flan-t5-large")  # LLM for reasoning

# SQLite database setup
DB_FILE = "patent_scores.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        # Table to store embeddings of unique patents
        conn.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            embedding BLOB
        )""")
        # Table to store comparison logs
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT,
            match_filename TEXT,
            similarity_score REAL,
            timestamp TEXT
        )""")
init_db()

# Extract all text from a PDF file
def extract_text(filepath):
    with pdfplumber.open(filepath) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

# Extract title, abstract, and claim 1 from a patent text
def extract_relevant_sections(text, filename="UNKNOWN"):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Try to extract title
    title = next((line for line in lines if re.search(r"(United States Patent|Patent No\\.|US\\d{7,})", line, re.I)), "")

    # Try to extract abstract
    abstract = ""
    for i, line in enumerate(lines):
        if re.match(r"(?i)^abstract$", line.strip()):
            abstract = " ".join(lines[i+1:i+5])
            break
    if not abstract:
        abstract = " ".join(lines[1:6])  # Fallback extraction

    # Try to extract claim 1 using common patterns
    claim_1 = ""
    claim_1_patterns = [
        r"(?i)^1[\\)\\.:]?\\s",
        r"(?i)^claim\\s*1[\\)\\.:]?\\s",
        r"(?i)^we claim",
        r"(?i)^what is claimed is",
    ]
    for i, line in enumerate(lines):
        if any(re.match(pat, line) for pat in claim_1_patterns):
            claim_1 = " ".join(lines[i:i+3])
            break

    return title.strip(), abstract.strip(), claim_1.strip()

# Safely truncate text for token-limited LLMs
def truncate_text(text, max_chars=1200):
    return text[:max_chars]

# Ask LLM to assess novelty based on selected sections and similarity score
def assess_novelty(test_text, match_text, similarity_score, test_filename="test", match_filename="match"):
    title1, abstract1, claim1 = extract_relevant_sections(test_text, test_filename)
    title2, abstract2, claim2 = extract_relevant_sections(match_text, match_filename)

    # Construct LLM prompt
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

# Save embedding to database
def store_embedding(filename, embedding):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT OR REPLACE INTO patents (filename, embedding) VALUES (?, ?)", (filename, embedding.tobytes()))

# Retrieve all stored embeddings
def fetch_embeddings():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT filename, embedding FROM patents")
        data = [(row[0], np.frombuffer(row[1], dtype=np.float32)) for row in cursor.fetchall()]
    return data

# Generate a hash token based on the text content
def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# On startup, embed all files in the patent directory into the DB
@app.on_event("startup")
def initialize_embeddings():
    for file in os.listdir(PATENT_DIR):
        if file.endswith(".pdf"):
            file_path = os.path.join(PATENT_DIR, file)
            text = extract_text(file_path)
            vec = model.encode([text])[0].astype(np.float32)
            store_embedding(file, vec)

# Upload endpoint to check for patent novelty
@app.post("/upload")
def upload_and_check(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text and generate embedding for the new document
    text = extract_text(file_path)
    query_vec = model.encode([text])[0]

    # Load all embeddings for similarity comparison
    embeddings = fetch_embeddings()
    if not embeddings:
        return JSONResponse(content={"error": "No prior patents in the database"}, status_code=400)

    # Build and search FAISS index
    vectors = np.array([e[1] for e in embeddings])
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    D, I = index.search(np.array([query_vec]), k=1)

    # Get the best match and compute similarity scores
    best_match_file, uniqueness_score = embeddings[I[0][0]][0], float(D[0][0])
    similarity_score = 1.0 - min(1.0, uniqueness_score)
    match_text = extract_text(os.path.join(PATENT_DIR, best_match_file))

    # Let the LLM assess novelty
    judgment = assess_novelty(text, match_text, similarity_score, "test_doc", best_match_file)
    document_id = generate_token(text)[:16]

    # Save result in the database
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO scores (document_id, match_filename, similarity_score, timestamp) VALUES (?, ?, ?, ?)",
                     (document_id, best_match_file, similarity_score, datetime.utcnow().isoformat()))

    # If not unique, delete file; else store and save embedding
    if uniqueness_score > SIMILARITY_THRESHOLD:
        os.remove(file_path)
    else:
        new_patent_path = os.path.join(PATENT_DIR, file.filename)
        shutil.move(file_path, new_patent_path)
        store_embedding(file.filename, query_vec.astype(np.float32))

    # Return final JSON response
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
