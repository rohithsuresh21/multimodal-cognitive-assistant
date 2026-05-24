from db import init_db
from ingest import ingest_knowledge
from retrieval import retrieve
from llm_engine import chat as llm_chat
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, json, shutil, datetime
from file_handler import extract_text, SUPPORTED_FILE_TYPES
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Multimodal Cognitive Assistant",
    description="Your assistant description here...",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = './uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    text: str
    history: list = []

ingested_files = []

@app.get('/', response_class=HTMLResponse)
async def serve_ui():
    with open('ui.html', 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.post('/upload')
async def upload_file(file: UploadFile):
    filename_str = str(file.filename)
    ext = os.path.splitext(filename_str)[1].lower()

    if ext not in SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported file type')

    dest = os.path.join(UPLOAD_DIR, filename_str)
    with open(dest, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(dest)
    txt_path = dest + '_extracted.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    ingest_knowledge(txt_path)
    word_count = len(text.split())
    ingested_files.append({'filename': filename_str, 'path': dest, 'word_count': word_count})

    return {
        'status': 'success',
        'file': filename_str,
        'type': ext.replace('.', ''),
        'word_count': word_count,
        'message': f'{filename_str} ingested successfully'
    }

@app.post('/chat')
async def chat_endpoint(req: ChatRequest):
    context = retrieve(req.text)
    return llm_chat(req.text, context=context, history=req.history)

@app.get("/files")
def get_files():
    return {"files": ingested_files}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
