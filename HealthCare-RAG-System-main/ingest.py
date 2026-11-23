# # ingest.py

import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from posthog import api_key

# ===========================
# CONFIGURATION
# ===========================
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "medical_records"

# Use the same setting as in rag.py
USE_CUSTOM_EMBEDDER = True
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DOCS_PATH = "docs"  # Folder containing patient records


# ===========================
# HELPER FUNCTIONS
# ===========================
def load_pdf_text(pdf_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error reading {pdf_path}: {e}")
        return ""


def chunk_text(text, chunk_size=800, overlap=100):
    """Splits text into overlapping chunks for better retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def get_client_and_collection():
    """Initializes Chroma client and collection (matching rag.py)."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    if USE_CUSTOM_EMBEDDER:
        hf_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
            #api_key = None
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
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(name=COLLECTION_NAME)

    return client, collection


# ===========================
# INGESTION LOGIC
# ===========================
def ingest_all():
    """Loads all PDFs from docs/, splits into chunks, and adds them to Chroma."""
    client, collection = get_client_and_collection()

    pdf_files = glob.glob(os.path.join(DOCS_PATH, "*.pdf"))
    if not pdf_files:
        print("⚠️ No PDF files found in 'docs/' folder.")
        return

    print(f"📚 Found {len(pdf_files)} PDF(s) in '{DOCS_PATH}'")

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"🧩 Processing: {filename}")

        text = load_pdf_text(pdf_path)
        if not text:
            continue

        chunks = chunk_text(text)
        metadatas = [{"source": filename, "patient_name": extract_patient_name(filename)} for _ in chunks]

        # Unique IDs for Chroma
        ids = [f"{filename}_{i}" for i in range(len(chunks))]

        # Add or update in collection
        try:
            collection.add(documents=chunks, metadatas=metadatas, ids=ids)
            print(f"✅ Ingested {len(chunks)} chunks from {filename}")
        except Exception as e:
            print(f"⚠️ Skipped {filename} (maybe already exists): {e}")

    print("🎉 Ingestion completed successfully.")


def extract_patient_name(filename):
    """
    Extracts a patient name from a filename.
    Example: 'John_Doe_Record.pdf' -> 'John Doe'
    """
    name_part = os.path.splitext(filename)[0]
    name_part = name_part.replace("_", " ")
    return name_part.strip().title()


# ===========================
# MAIN ENTRY POINT
# ===========================
if __name__ == "__main__":
    os.makedirs(DOCS_PATH, exist_ok=True)
    ingest_all()
