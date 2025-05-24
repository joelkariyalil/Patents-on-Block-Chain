# 🧠 Decentralized Patent Submission Platform

This project is a **modular, secure, and fully containerized** system designed to facilitate the submission, deduplication, hashing, and decentralized storage of patents using **FastAPI**, **Docker**, **Redis**, **PostgreSQL**, and **Web3.Storage/IPFS**.

---

## 🚀 Features

- 🧠 **AI Agent Service**  
  Detects and prevents duplicate patent submissions using a similarity search in the DB and web.

- 🌍 **Decentralized Storage with IPFS**  
  Uses [Web3.Storage](https://web3.storage/) to pin files permanently to IPFS. (Currently, locally storing the files)

- 🔒 **FastAPI Backend**  
  Handles user interaction, submission endpoints, and communication between services.

- 🐘 **PostgreSQL DB**  
  Stores file metadata, hashes, timestamps, and IPFS CIDs.

- ⚡ **Redis Cache**  
  Stores recent hashes to accelerate duplication checks.

- 🐳 **Docker & Docker Compose**  
  Each service runs in an isolated container, ensuring modularity, security, and scalability.

---

## 🧱 Architecture

Refer to the system design file for a complete overview of how the services interact:  
➡️ **[System Design Diagram](https://github.com/joelkariyalil/Patents-on-Block-Chain/blob/backend/Sketches/system-design.png?raw=true)**
