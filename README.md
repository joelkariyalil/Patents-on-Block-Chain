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
# Keep it Running, it might shoot some rubbish outputs, end goal is it will show uvicorn started at: https:\\ (our backend URL)
```

### 2. Compile + Deploy Smart Contract

```bash
cd blockchain
npx hardhat node
# In another terminal:
npx hardhat run scripts/deploy.js --network localhost
# Make sure both things are running in terminal (Don't press stop or kill)
``` 
### 3. Start Frontend

```bash
cd react-client
npm start
```

Visit: `http://localhost:3000` (Visit this only if webpage not opens automatically)

### 4. Configure React

* Update `CONTRACT_ADDRESS` in `MetaMaskSubmit.jsx` (This file is located in react-client/src/components)
* Ensure IPFS Pinata keys are correctly set in `ipfs_upload.py`

---

## 🦊 MetaMask & Hardhat Setup

To interact with the smart contract using MetaMask and the Hardhat local blockchain:

### 1. Import Hardhat Wallets into MetaMask

* Open MetaMask ➜ Click on account icon ➜ `Import Account`
* Paste one of the private keys from Hardhat output (from the terminal where we ran "npx hardhat node")
* Repeat to import multiple wallets if needed (for testing multiple users)

### 2. Add Localhost Network to MetaMask

Go to MetaMask ➜ `Settings` ➜ `Networks` ➜ `Add Network` ➜ Fill in:

```
Network Name:      Localhost 8545
New RPC URL:       http://127.0.0.1:8545
Chain ID:          31337
Currency Symbol:   ETH
```

Click Save. Now your MetaMask is ready to interact with Hardhat.

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

Team: PatentAI (ETH Dublin-25)

Open-source contributions welcome! PRs, feature requests and forks appreciated.

---

## ✉️ License

MIT License. See `LICENSE` file.

---

## 📈 Project Video

[![Watch the Demo](https://img.youtube.com/vi/NBk4JuVnN9Y/0.jpg)](https://youtu.be/NBk4JuVnN9Y)

## Contributions

- Front End and UI + Working Project Demo - Ujwal Mojidra  
- Agentic AI and LLMs - Rahul Babu and Sarosh Farhan  
- Backend and Containerization - Joel Thomas Chacko  
