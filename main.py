import os, shutil, json, datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingest import ingest_knowledge
from retrieval import retrieve
from llm_engine import chat as llm_chat
from file_handler import extract_text, SUPPORTED_TYPES

app = FastAPI(title="Multimodal Cognitive Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ingested_files = []   # in-memory log of uploaded files

# ── Models ──────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    text: str
    history: list = []

# ── Routes ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the built-in web UI."""
    return HTMLResponse(content=open("ui.html").read())


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept a file, save it, extract text, ingest into local Qdrant."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400,
            detail=f"Unsupported type '{ext}'. Allowed: {', '.join(SUPPORTED_TYPES)}")

    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        text = extract_text(dest)
        word_count = len(text.split())

        # Write text to a temp .txt so ingest_knowledge can read it
        txt_path = dest + "_extracted.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        ingest_knowledge(txt_path)

        ingested_files.append({
            "filename": file.filename,
            "type": ext,
            "word_count": word_count,
            "uploaded_at": datetime.datetime.now().isoformat()
        })

        return {"status": "success", "file": file.filename,
                "word_count": word_count,
                "message": f"Ingested {word_count} words from {file.filename}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    """Return all ingested files."""
    return {"files": ingested_files}


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """RAG chat: retrieve context from local DB, then ask Mistral."""
    context = retrieve(req.text)
    result = llm_chat(req.text, context=context, history=req.history)
    return result


@app.get("/health")
async def health():
    return {"status": "ok", "files_ingested": len(ingested_files)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
