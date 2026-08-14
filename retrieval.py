from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

DB_PATH = "./local_qdrant"
COLLECTION_NAME = "personal_memory"
TOP_K = 5

client = QdrantClient(path=DB_PATH)
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query: str) -> str:
    """Search local Qdrant for the most relevant chunks for a given query."""
    try:
        query_vector = encoder.encode(query).tolist()
        results = client.search(
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
