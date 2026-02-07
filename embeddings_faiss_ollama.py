import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


def load_chunks(file_path="output.txt", chunk_size=200, overlap=50):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


if __name__ == "__main__":
    print("🔹 Loading chunks...")
    chunks = load_chunks()
    print(f"✅ Loaded {len(chunks)} chunks")

    print("🔹 Loading embedding model (first time takes a few minutes)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = model.encode(chunks, convert_to_numpy=True).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, "faiss.index")

    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("✅ FAISS index rebuilt successfully")
