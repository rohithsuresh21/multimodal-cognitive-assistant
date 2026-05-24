import os
import tiktoken
import db
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

DB_PATH = "./local_qdrant_v2"
COLLECTION_NAME = "personal_memory"

print("Loading local embedding model (all-MiniLM-L6-v2)...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def setup_database():
    client = db.init_db()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"[+] Collection '{COLLECTION_NAME}' created successfully.")
    else:
        print(f"[~] Collection '{COLLECTION_NAME}' already exists.")
    return client

def chunk_text(file_path: str, max_tokens: int = 300, overlap: int = 50) -> list:
    if not os.path.exists(file_path):
        print(f"[-] Error: {file_path} not found.")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text.strip())
        start += max_tokens - overlap

    return [c for c in chunks if c]

def ingest_knowledge(file_path: str):
    client = setup_database()
    chunks = chunk_text(file_path)

    if not chunks:
        print("[-] No text chunks to ingest.")
        return

    print(f"Vectorizing {len(chunks)} text fragments...")
    points = []
    for chunk in chunks:
        vector = encoder.encode(chunk).tolist()
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": chunk, "source": file_path}
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("[+] Long-term memory ingestion complete! Data saved to disk.")

if __name__ == "__main__":
    ingest_knowledge("knowledge.txt")