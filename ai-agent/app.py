from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import hashlib
import shutil
import numpy as np
import pdfplumber
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re
import redis
import json

app = FastAPI()

# Constants and model initialization
UPLOAD_DIR = "uploaded_docs"         # Temporary storage for uploaded files
PATENT_DIR = "patents"               # Directory to store accepted unique patents
SIMILARITY_THRESHOLD = 0.3           # Threshold for deciding novelty based on L2 distance
VECTOR_DIM = 384                     # Dimension of all-MiniLM-L6-v2 embeddings

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PATENT_DIR, exist_ok=True)

# Initialize models
model = SentenceTransformer("all-MiniLM-L6-v2")   # For semantic vector generation
llm = pipeline("text2text-generation", model="google/flan-t5-large")  # LLM for reasoning

# Redis configuration
REDIS_HOST = "agent-response-db"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Store embedding in Redis
def store_embedding(filename, embedding):
    key = f"patent:{filename}"
    # Store as list since Redis can't store numpy arrays directly
    redis_client.hset(
        key,
        mapping={
            "filename": filename,
            "embedding": json.dumps(embedding.tolist())
        }
    )

# Find most similar patent
def find_similar_patent(query_vec):
    best_match = None
    min_distance = float('inf')
    
    # Get all patent keys
    for key in redis_client.keys("patent:*"):
        data = redis_client.hgetall(key)
        if data and "embedding" in data:
            stored_vec = np.array(json.loads(data["embedding"]))
            distance = np.linalg.norm(query_vec - stored_vec)
            if distance < min_distance:
                min_distance = distance
                best_match = data["filename"]
    
    return best_match, min_distance if best_match else (None, None)

# Extract text from PDF
def extract_text(filepath):
    with pdfplumber.open(filepath) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

# Extract relevant sections from patent text
def extract_relevant_sections(text, filename="UNKNOWN"):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Try to extract title
    title = next((line for line in lines if re.search(r"(United States Patent|Patent No\.|US\d{7,})", line, re.I)), "")

    # Try to extract abstract
    abstract = ""
    for i, line in enumerate(lines):
        if re.match(r"(?i)^abstract$", line.strip()):
            abstract = " ".join(lines[i+1:i+5])
            break
    if not abstract:
        abstract = " ".join(lines[1:6])  # Fallback extraction

    # Try to extract claim 1
    claim_1 = ""
    claim_1_patterns = [
        r"(?i)^1[\)\.]?\s",
        r"(?i)^claim\s*1[\)\.]?\s",
        r"(?i)^we claim",
        r"(?i)^what is claimed is",
    ]
    for i, line in enumerate(lines):
        if any(re.match(pat, line) for pat in claim_1_patterns):
            claim_1 = " ".join(lines[i:i+3])
            break

    return title.strip(), abstract.strip(), claim_1.strip()

# Assess novelty using LLM
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

# Generate hash token
def generate_token(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Initialize Redis and load existing patents on startup
@app.on_event("startup")
async def startup_event():
    # Clear existing embeddings
    for key in redis_client.keys("patent:*"):
        redis_client.delete(key)
    
    # Load all existing patents
    for file in os.listdir(PATENT_DIR):
        if file.endswith(".pdf"):
            file_path = os.path.join(PATENT_DIR, file)
            text = extract_text(file_path)
            vec = model.encode([text])[0].astype(np.float32)
            store_embedding(file, vec)

# Upload and check endpoint
@app.post("/upload")
async def upload_and_check(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract text and generate embedding
        text = extract_text(file_path)
        query_vec = model.encode([text])[0].astype(np.float32)

        # Find most similar patent
        best_match_file, uniqueness_score = find_similar_patent(query_vec)
        
        if not best_match_file:
            return JSONResponse(
                content={"error": "No prior patents in the database"},
                status_code=400
            )
        
        # Convert numpy types to Python native types
        uniqueness_score = float(uniqueness_score)
        similarity_score = float(1.0 - min(1.0, uniqueness_score / 10.0))  # Normalize distance to similarity
        
        # Get matched patent text
        match_text = extract_text(os.path.join(PATENT_DIR, best_match_file))
        
        # Get LLM judgment
        judgment = assess_novelty(text, match_text, similarity_score, "test_doc", best_match_file)
        document_id = generate_token(text)[:16]
        
        # Handle file storage
        is_unique = bool(uniqueness_score > SIMILARITY_THRESHOLD)  # Convert numpy.bool to Python bool
        if is_unique:
            os.remove(file_path)
        else:
            new_patent_path = os.path.join(PATENT_DIR, file.filename)
            shutil.move(file_path, new_patent_path)
            store_embedding(file.filename, query_vec)
        
        # Return response with native Python types
        return {
            "document_id": document_id,
            "uniqueness_score": uniqueness_score,
            "is_unique": is_unique,
            "matched_patent": {
                "filename": best_match_file,
                "similarity_score": similarity_score
            },
            "agent_judgment": judgment,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "token": generate_token(text)
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(
            content={"error": f"Error processing request: {str(e)}"},
            status_code=500
        )

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AI agent is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 