import threading

import torch

# Keep PyTorch memory low on small (Render free 512MB) instances.
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

DB_PATH = "./local_qdrant"
COLLECTION_NAME = "personal_memory"
TOP_K = 5

_lock = threading.Lock()
_client = None
_encoder = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = QdrantClient(path=DB_PATH)
    return _client


def _get_encoder() -> SentenceTransformer:
    global _encoder
    if _encoder is None:
        with _lock:
            if _encoder is None:
                _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return _encoder


def retrieve(query: str) -> str:
    """Search local Qdrant for the most relevant chunks for a given query."""
    try:
        query_vector = _get_encoder().encode(query).tolist()
        results = _get_client().search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=TOP_K
        )
        if not results:
            return ""
        context_parts = []
        for r in results:
            text = r.payload.get("text", "")
            source = r.payload.get("source", "unknown")
            score = round(r.score, 3)
            context_parts.append(f"[source: {source} | score: {score}]\n{text}")
        return "\n\n".join(context_parts)
    except Exception as e:
        print(f"[-] Retrieval error: {e}")
        return ""


if __name__ == "__main__":
    result = retrieve("What is the capital of France?")
    print(result)
