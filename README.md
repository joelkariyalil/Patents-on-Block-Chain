# 🔍 PatentAI: Blockchain-Powered Patent Novelty Checker

PatentAI is a privacy-first, AI-powered platform to verify the novelty of patent documents and record unique results securely on the blockchain. Designed for inventors, researchers, and IP professionals, it combines semantic similarity detection, LLM-based judgment, decentralized storage (IPFS), and smart contracts for transparent patent logging.

---

## ✨ Features

* 🧠 **AI-Powered Novelty Detection** using SBERT and semantic search (FAISS)
* ✨ **LLM Agent Reasoning** to classify as Novel / Modified / Plagiarized
* 💾 **Secure Result Storage** using IPFS
* 🚀 **MetaMask Blockchain Submission** via Smart Contracts
* 📖 Tailored for **USPTO-style patent documents**
* 📈 Sleek React UI with animated gradient themes

---

## 🌐 Project Structure

```
Patents-on-Block-Chain/
├── backend/            # FastAPI backend (LLM, vector DB, IPFS integration)
├── blockchain/         # Solidity contract + Hardhat config
├── react-client/       # Frontend in React.js
```

---

## ⚙️ Tech Stack

* **Frontend**: React.js, Tailwind CSS (minimal)
* **Backend**: FastAPI, SentenceTransformers, Transformers (HuggingFace), FAISS, pdfplumber
* **Blockchain**: Solidity, Hardhat, ethers.js
* **Storage**: IPFS (via Pinata), SQLite

---

## 🚫 Requirements

### Backend

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt**

```
fastapi
uvicorn
sentence-transformers
transformers
faiss-cpu
pdfplumber
python-multipart
sqlite3  # comes built-in
requests
```

### Frontend

```bash
cd react-client
npm install
```

### Blockchain

```bash
cd blockchain
npm install
npx hardhat compile
```

---

## 🔧 How to Run

### 1. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

### 2. Start Frontend

```bash
cd react-client
npm start
```

Visit: `http://localhost:3000`

### 3. Compile + Deploy Smart Contract

```bash
cd blockchain
npx hardhat node
# In another terminal:
npx hardhat run scripts/deploy.js --network localhost
```

### 4. Configure React

* Update `CONTRACT_ADDRESS` in `MetaMaskSubmit.jsx`
* Ensure IPFS Pinata keys are correctly set in `ipfs_upload.py`

---

## 💡 How It Works

1. Upload a patent document (PDF)
2. Backend extracts title, abstract, and claims
3. SBERT encodes the full text and compares with prior embeddings (FAISS)
4. LLM (FLAN-T5) provides judgment: (a) Clearly novel / (b) Obvious modification / (c) Plagiarized
5. If unique, user can upload result to IPFS
6. If still unique, result can be stored on blockchain with MetaMask

---

## 🎓 Built for ETHDublin Hackathon 2025

Team: Ujwal Mojidra & Team

Open-source contributions welcome! PRs, feature requests and forks appreciated.

---

## ✉️ License

MIT License. See `LICENSE` file.

---

## 📈 Sample Screenshot

![screenshot](./react-client/public/sample_ui.png)
