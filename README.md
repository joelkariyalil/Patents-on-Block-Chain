# Patent Similarity API (FastAPI + Redis)

This project provides a REST API for checking the novelty of patent documents using semantic similarity search and LLM-based reasoning. It uses FastAPI for the backend and Redis for fast vector storage and retrieval.

---

## 🚀 Features
- Upload patent PDFs and check for novelty against prior art
- Semantic similarity search using Sentence Transformers
- LLM-based reasoning for novelty assessment
- Fast, scalable, and stateless with Redis backend
- Dockerized for easy deployment

---

## 🛠️ Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) Python 3.9+ if running locally without Docker

---

## ⚡ Quickstart (Recommended: Docker Compose)

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Build and start the stack:**
   ```sh
   docker-compose up --build
   ```
   This will start both the FastAPI app and Redis. The API will be available at [http://localhost:8000](http://localhost:8000).

3. **Access the API docs:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.
   - Or [http://localhost:8000/redoc](http://localhost:8000/redoc) for ReDoc.

4. **Stopping the stack:**
   ```sh
   docker-compose down
   ```

---

## 🧑‍💻 Local Development (Without Docker)

1. **Install Redis and start the server** (if not using Docker):
   - On macOS: `brew install redis && brew services start redis`
   - On Ubuntu: `sudo apt-get install redis-server && sudo service redis-server start`

2. **Create and activate a Python virtual environment:**
   ```sh
   python3 -m venv .env
   source .env/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the FastAPI app:**
   ```sh
   uvicorn PatentAgent_redis:app --reload
   ```

---

## 📂 Project Structure

- `PatentAgent_redis.py` — Main FastAPI app (uses Redis)
- `requirements.txt` — Python dependencies
- `Dockerfile` — Docker build for the API
- `docker-compose.yml` — Multi-container setup (API + Redis)
- `uploaded_docs/` — Temporary storage for uploads (auto-created)
- `patents/` — Storage for accepted unique patents (auto-created)

---

## 📑 API Endpoints

### 1. `POST /upload`
**Description:** Upload a patent PDF to check for novelty.

- **Request:**
  - `file`: PDF file (form-data)

- **Response:**
  - `document_id`: Unique ID for the uploaded document
  - `uniqueness_score`: L2 distance to the closest prior art
  - `is_unique`: Boolean, whether the document is considered unique
  - `matched_patent`: Info about the closest match
  - `agent_judgment`: LLM's novelty assessment
  - `timestamp`: ISO timestamp
  - `token`: Hash of the document

- **Example (using curl):**
  ```sh
  curl -X POST "http://localhost:8000/upload" \
    -F "file=@/path/to/your/patent.pdf"
  ```

### 2. API Documentation
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📝 Notes
- The API will store unique patents in the `patents/` directory and their embeddings in Redis.
- If a patent is not unique, it will not be stored.
- Redis is used for fast vector search; no data is persisted between container restarts unless you mount a volume for Redis data.
- The `/upload` endpoint is the main entry point for checking patent novelty.

---

## 🧩 Customization
- You can adjust the similarity threshold in `PatentAgent_redis.py` (`SIMILARITY_THRESHOLD`)
- To use a different model, change the `SentenceTransformer` or LLM pipeline in the code.

---

## 🆘 Troubleshooting
- **Redis connection errors:** Ensure Redis is running and accessible at the configured host/port.
- **Dependency issues:** Rebuild the Docker image with `docker-compose build --no-cache`.
- **File upload issues:** Ensure the `uploaded_docs/` and `patents/` directories are writable.
