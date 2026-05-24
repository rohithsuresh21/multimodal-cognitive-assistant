from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import db

DB_PATH = "./local_qdrant_v2"
COLLECTION_NAME = "personal_memory"
TOP_K = 5
MIN_SCORE = 0.3
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query: str) -> str:
    query_vector = encoder.encode(query).tolist()

    response = db.client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=TOP_K
    )

    results = response.points
    if not results:
        return ""

    context_parts = []
    for r in results:
        if r.score < MIN_SCORE:
            continue
        text = r.payload.get("text", "").strip()
        source = r.payload.get("source", "unknown")
        if text:
            context_parts.append(f"[Source: {source}]\n{text}")

    return "\n\n".join(context_parts) if context_parts else ""