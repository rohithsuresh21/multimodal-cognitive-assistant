import os
import csv

SUPPORTED_TYPES = {".txt", ".pdf", ".docx", ".csv"}

def extract_text(file_path: str) -> str:
    """Auto-detects file type and extracts plain text."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_TYPES)}")

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise ImportError("Install pypdf: pip install pypdf")

    elif ext == ".docx":
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise ImportError("Install python-docx: pip install python-docx")

    elif ext == ".csv":
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(", ".join(row))
        return "\n".join(rows)

    return ""
