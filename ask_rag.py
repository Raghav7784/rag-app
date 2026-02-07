import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import subprocess


def search_faiss(question, top_k=1):
    index = faiss.read_index("faiss.index")

    with open("chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    q_embedding = model.encode([question]).astype("float32")

    distances, indices = index.search(q_embedding, top_k)
    return [chunks[i] for i in indices[0]]


def ask_ollama(context, question):
    prompt = f"""
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""

    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        text=True
    )

    return result.stdout


if __name__ == "__main__":
    question = "What is this document about?"

    relevant_chunks = search_faiss(question, top_k=1)
    context = "\n".join(relevant_chunks)

    answer = ask_ollama(context, question)

    print("\n🤖 Answer:\n")
    print(answer)
