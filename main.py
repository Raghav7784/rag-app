# backend/main.py
import os
import pickle
import faiss
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# RAG system setup
app = FastAPI()

DATA = "backend/data"
PDF = f"{DATA}/knowledge.pdf"      # your PDF file
IDX = f"{DATA}/faiss.index"
CHUNKS = f"{DATA}/chunks.pkl"

# Ensure data folder exists
os.makedirs(DATA, exist_ok=True)

# FastAPI model for chat
class Query(BaseModel):
    message: str

# Load embeddings + FAISS
index, chunks, model = None, None, None

def load_system():
    global index, chunks, model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load FAISS index
    if os.path.exists(IDX) and os.path.exists(CHUNKS):
        index = faiss.read_index(IDX)
        with open(CHUNKS, "rb") as f:
            chunks = pickle.load(f)
        print("✅ Loaded FAISS index and chunks")
    else:
        print("⚠️ FAISS index or chunks not found. Run embeddings first.")
        index, chunks = None, None

# Simple chunking
def chunk_text(text, chunk_size=200, overlap=50):
    result = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        result.append(text[start:end])
        start = end - overlap
    return result

# Search FAISS
def retrieve(query, top_k=1):
    if index is None:
        raise RuntimeError("FAISS index not loaded")
    q_emb = model.encode([query]).astype("float32")
    _, idx = index.search(q_emb, top_k)
    return "\n".join(chunks[i] for i in idx[0])

# Ingest PDF text into FAISS
@app.post("/ingest")
def ingest():
    global index, chunks
    if not os.path.exists(PDF):
        return {"error": f"{PDF} not found"}

    # Convert PDF to text
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(PDF)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        return {"error": str(e)}

    # Chunking
    chunks = chunk_text(text)

    # Build embeddings + FAISS
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks).astype("float32")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save FAISS + chunks
    faiss.write_index(index, IDX)
    with open(CHUNKS, "wb") as f:
        pickle.dump(chunks, f)

    return {"status": "Ingested successfully", "chunks": len(chunks)}

# Chat endpoint
@app.post("/chat")
def chat(q: Query):
    if index is None or chunks is None or model is None:
        load_system()

    ctx = retrieve(q.message)
    # Simple answer: return context + question (replace with LLM later)
    answer = f"Context:\n{ctx}\n\nQuestion:\n{q.message}"
    return {"answer": answer}

# Load system on startup
load_system()
