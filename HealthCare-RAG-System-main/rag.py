# # rag.py

import os
import chromadb
from chromadb.utils import embedding_functions
from ollama import chat
from posthog import api_key

# ===========================
# CONFIGURATION
# ===========================
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "medical_records"

# Toggle this flag to switch modes:
# True  → use explicit HuggingFaceEmbeddings
# False → use Chroma’s default internal embedder
USE_CUSTOM_EMBEDDER = True

# Choose the embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ===========================
# INITIALIZATION
# ===========================
def get_client_and_collection():
    """Initializes Chroma client and collection depending on mode."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    if USE_CUSTOM_EMBEDDER:
        hf_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        try:
            collection = client.get_collection(
                name=COLLECTION_NAME, embedding_function=hf_embedder
            )
        except Exception:
            collection = client.create_collection(
                name=COLLECTION_NAME, embedding_function=hf_embedder
            )
    else:
        # No external embedder — use Chroma’s internal defaults
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(name=COLLECTION_NAME)

    return client, collection


# ===========================
# RETRIEVAL
# ===========================
def retrieve_docs(query: str, top_k: int = 3):
    """Retrieves the top-k most relevant documents."""
    _, collection = get_client_and_collection()

    if USE_CUSTOM_EMBEDDER:
        # Explicit embedding
        results = collection.query(
            query_texts=[query],  # text will be embedded using our custom embedder
            n_results=top_k
        )
    else:
        # Implicit embedding (Chroma default)
        results = collection.query(query_texts=[query], n_results=top_k)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return docs, metas


# ===========================
# GENERATION (Ollama)
# ===========================
def generate_answer(question: str, docs: list[str], memory: dict):
    """Uses Ollama to generate an answer based on retrieved docs and chat memory."""

    # Build context
    context_text = "\n\n".join(docs)
    history_text = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in memory.get("history", [])])

    prompt = f"""
You are a medical assistant AI that answers based on clinical records.
Be accurate and concise.

Conversation so far:
{history_text}

Question: {question}

Relevant documents:
{context_text}

Answer:"""

    response = chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response["message"]["content"].strip()
    return answer


# ===========================
# MAIN RAG FUNCTION
# ===========================
def answer_question(question: str, memory: dict):
    """Main RAG workflow: retrieve → generate → update memory."""
    docs, metas = retrieve_docs(question)
    answer = generate_answer(question, docs, memory)

    # Track patient context (very simple heuristic)
    patient_name = None
    for meta in metas:
        if "patient_name" in meta:
            patient_name = meta["patient_name"]
            break

    # Update conversation memory
    if "history" not in memory:
        memory["history"] = []
    memory["history"].append({"user": question, "bot": answer})

    if patient_name:
        memory["current_patient"] = patient_name

    return answer, docs, metas, memory


# ===========================
# TEST (for manual execution)
# ===========================
if __name__ == "__main__":
    q = "What medications is John Doe currently taking?"
    memory = {"history": [], "current_patient": None}
    ans, docs, metas, memory = answer_question(q, memory)
    print("Answer:\n", ans)
    print("\nSources:\n", metas)
    print("\nMemory:\n", memory)
