import os 
import csv
from pypdf import PdfReader
from docx import Document

SUPPORTED_FILE_TYPES = ['.csv', '.txt', '.pdf', '.docx']

def extract_text(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {extension}")
    if extension == '.csv':
        return extract_text_from_csv(file_path)
    if extension == '.txt':
        return extract_text_from_txt(file_path)
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    if extension == '.docx':
        return extract_text_from_docx(file_path)
    raise ValueError(f"Text extraction not implemented for file type: {extension}")

def extract_text_from_csv(file_path: str) -> str:
    text = ""
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            text += ' '.join(row) + '\n'
    return text

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return '\n'.join(page.extract_text() or '' for page in reader.pages)

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())