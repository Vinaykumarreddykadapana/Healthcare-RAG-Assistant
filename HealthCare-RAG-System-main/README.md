# 🏥 Clinical Records RAG System

This project implements a Retrieval-Augmented Generation (RAG) system for querying medical records using **Python, Flask, ChromaDB, and Ollama**.

## 🚀 Features
- Upload and index patient medical records
- Query using natural language with contextual memory
- Visual and interactive UI (Flask + HTML + CSS)
- Works fully offline with Ollama + local embeddings

## 🧠 How It Works
1. `ingest.py` → Processes medical records and stores embeddings in ChromaDB.
2. `rag.py` → Handles retrieval and LLM answer generation.
3. `ui_flask.py` → Web UI for interaction.
4. `main.py` → Runs the full app from one entry point.

In the Web UI, from the left side panel, run the Ingest first. Then write your query.

## 🛠️ Setup
```bash
python -m venv .venv
source .venv/bin/activate   # on Linux/macOS
.venv\Scripts\activate      # on Windows
pip install -r requirements.txt
