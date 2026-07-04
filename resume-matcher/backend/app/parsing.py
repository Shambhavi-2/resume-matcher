"""
Extracts plain text from uploaded resume files, then splits text into
semantically useful chunks (roughly paragraph/bullet level) that the
embedding step can score independently.
"""
import io
import re
from typing import List

import pdfplumber
from docx import Document


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(content)
    elif lower.endswith(".docx"):
        return _extract_docx(content)
    elif lower.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def _extract_pdf(content: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


def chunk_text(text: str, min_chars: int = 40) -> List[str]:
    """
    Splits raw text into chunks along blank lines / bullet markers, then
    drops fragments too short to be meaningful (e.g. stray page numbers).
    """
    raw_chunks = re.split(r"\n\s*\n|\n(?=[•\-\*]\s)", text)
    chunks = []
    for c in raw_chunks:
        cleaned = " ".join(c.split())
        if len(cleaned) >= min_chars:
            chunks.append(cleaned)
    # Fallback: if splitting produced nothing usable, treat the whole text as one chunk
    if not chunks and text.strip():
        chunks = [" ".join(text.split())]
    return chunks
