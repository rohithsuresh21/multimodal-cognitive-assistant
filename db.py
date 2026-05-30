from qdrant_client import QdrantClient

DB_PATH = "./local_qdrant_v2"
COLLECTION_NAME = "personal_memory"
client = None  

def init_db():
    global client
    if client is None:
        client = QdrantClient(path=DB_PATH)
    return client 
