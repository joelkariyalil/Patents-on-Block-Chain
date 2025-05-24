# Patent Uniqueness Verifier – Agentic AI System

This repository contains an agentic AI-powered pipeline that evaluates the **novelty** of a test patent document by comparing it to an existing corpus of patents. It combines semantic search using FAISS and dense embeddings with large language model (LLM) reasoning to assess whether a document is:
- ✅ Clearly novel  
- ⚠️ An obvious modification  
- ❌ Possibly plagiarized

---

## 🚀 Features

- 📄 **Patent PDF extraction** using `pdfplumber`
- 🔍 **Semantic vector comparison** using `SentenceTransformer + FAISS`
- 🤖 **Agentic AI judgment** via Hugging Face LLM (`flan-t5-large`)
- 🧠 Smart heuristic to detect non-patent or fake documents
- ✅ JSON output with scores, verdict, and agent commentary
- 📦 Modular and extensible architecture

---

## 🧩 Architecture

```plaintext
[PDF Document]
     ↓
[Text Extraction]
     ↓
[Embedding via MiniLM]
     ↓
[FAISS Similarity Check]
     ↓
[LLM Prompt → Judgment]
     ↓
[JSON Output with Scores & Token]
```

## Project Structure
```plaintext
├── patents/                # Folder with known patents (PDFs)
├── Test_Dupe.pdf           # Test file to verify novelty
├── uniqueness_result.json  # Output result (verdict & metadata)
├── main.py                 # Main Python script (this repo)
└── README.md               # You are here
```

## Setup Instructions
### Step 1: Clone this repo

```
git clone https://github.com/yourusername/patent-ai-agent.git
cd patent-ai-agent
```

### Step 2: Install Requirements

```
pip install pdfplumber faiss-cpu numpy sentence-transformers transformers
```

### Step 3: Add patents collected to /patents folder

```
1. Download all patents required for training
2. Make a folder called patents
3. Copy the downloaded patents to this folder
```

### Step 4: Run the agent

```
python PatentAgent_V4.py
```

## Output Format (JSON)
```
{
  "document_id": "ea74f8ad74ee6412",
  "uniqueness_score": 0.0,
  "is_unique": false,
  "matched_patent": {
    "filename": "US9302393.pdf",
    "similarity_score": 1.0
  },
  "agent_judgment": "(c) Possibly plagiarized",
  "timestamp": "2025-05-24T10:14:44.913045Z",
  "token": "ea74f8ad74ee6412d64cc6085a7a614e9f71b2b28413d7e3cf3990dc3c3e8057",
  "diagnostic": ""
}
```
## What makes this agentic?

This project follows the agentic AI pattern:

- Perceives input (PDF → text)
- Reasons about novelty using LLMs
- Acts autonomously (delete or keep file)
- Stores knowledge (via FAISS)
- Grows its internal database without supervision

## Notes

- Patent documents should be in machine-readable PDF format.
- LLM used is google/flan-t5-large (via Hugging Face)
- Vector model used is all-MiniLM-L6-v2 from Sentence Transformers
