# 🛡️ Secure Examination Workflow using Blockchain & IPFS

[![Research Paper](https://img.shields.io/badge/Research-IJARCCE-blue)](https://doi.org/10.17148/IJARCCE.2026.15170)
[![Python](https://img.shields.io/badge/Backend-Python%203.12-green)](https://www.python.org/)
[![Blockchain](https://img.shields.io/badge/Blockchain-Ethereum%2F%20Solidity-blueviolet)](https://soliditylang.org/)

### 🎓 Academic Research Publication
 **IJARCCE (Vol. 15, Issue 4, 2026)**.
* **DOI:** $10.17148/IJARCCE.2026.15170$
* **Context:** Final Year Master’s Project | Bangalore Institute of Technology (BIT)

---

## 📖 Project Overview
Traditional examination systems are vulnerable to leaks and unauthorized access. This **Decentralized Application (dApp)** introduces a tamper-proof workflow for managing exam papers. By combining **Ethereum Smart Contracts**, **IPFS decentralized storage**, and **AES-128 encryption**, we ensure that papers are only accessible to authorized superintendents at a pre-defined timestamp.

---

## 🚀 Key Features
* **Decentralized Storage:** Exam papers are stored on IPFS, ensuring no single point of failure.
* **Hybrid Encryption:** Files are encrypted locally using **AES-128 (Fernet)** before being uploaded to IPFS.
* **Smart Contract Governance:** All paper metadata, ownership, and unlock timers are enforced by Solidity contracts.
* **RBAC (Role-Based Access Control):** * **Teacher:** Uploads and encrypts papers.
    * **COE (Controller of Exams):** Finalizes papers and assigns Superintendents.
    * **Superintendent:** Decrypts and downloads papers only after the "Unlock Time."

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python (Flask), SQLAlchemy |
| **Blockchain** | Solidity, Web3.py, Ganache |
| **Storage** | IPFS (InterPlanetary File System) |
| **Security** | Cryptography (AES-128 / Fernet) |
| **Frontend** | HTML5, CSS3, Jinja2 |

---

## 📂 Folder Structure
```text
Secure-Examination-Blockchain/
├── contracts/             # Solidity Smart Contracts
├── static/                # CSS & Frontend Assets
├── templates/             # HTML Templates (Flask)
├── .env.example           # Template for Environment Variables
├── .gitignore             # Git ignore rules (venv, .env, etc.)
├── final.py               # Main Application Logic
├── contract_abi.json      # Compiled Smart Contract ABI
└── requirements.txt       # Project Dependencies

---

## 🔧 Setup & Installation

### 1. Prerequisites
Before running the application, ensure you have the following installed:
* **Python 3.12+**
* **Ganache** (Local Blockchain)
* **IPFS Desktop** (Ensure the API is running on port 5001)

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/tahirahmed1718/Secure-Examination-Blockchain.git](https://github.com/tahirahmed1718/Secure-Examination-Blockchain.git)
cd Secure-Examination-Blockchain

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

---

### 3. Configuration
Locate the .env.example file in the root directory.

Rename the file to exactly .env.

Open the .env file and replace the placeholders with your credentials:

Plaintext
# Blockchain Credentials
PRIVATE_KEY=your_ganache_private_key
CONTRACT_ADDRESS=your_deployed_contract_address

# Storage & Network
GANACHE_URL=[http://127.0.0.1:7545](http://127.0.0.1:7545)
IPFS_API_URL=[http://127.0.0.1:5001](http://127.0.0.1:5001)

---

### 4. Execution
```bash
python final.py

---

🛡️ Security Note
IMPORTANT: This project utilizes environment variables (.env) to manage sensitive information like private keys. Never commit your .env file to version control. The .gitignore in this repository is pre-configured to block this file. Always refer to .env.example when setting up new environments.

🎓 Future Scope
Cloud Migration: Transitioning the local Ganache environment to AWS Managed Blockchain (AMB) for enterprise-grade scalability.

Serverless Integration: Implementing AWS Lambda triggers to automate paper destruction post-examination.

Multi-Sig Approval: Enhancing smart contract logic to require multiple digital signatures before paper finalization.

Zero-Knowledge Proofs (ZKP): Integrating ZKPs to verify credentials without exposing wallet identities.
