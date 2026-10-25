import os
from typing import List, Dict
import PyPDF2

def process_pdf(
    file_path: str | os.PathLike,
    max_records: int | None = None,
) -> List[Dict[str, str]]:
    """Extract text from each page of a PDF.

    Returns a list of dictionaries, each with keys ``page`` (1‑based index)
    and ``text`` (the raw extracted string). Empty pages are omitted.
    """
    reader = PyPDF2.PdfReader(file_path)
    data = []
    for i, page in enumerate(reader.pages, start=1):
        if max_records is not None and i > max_records:
            break
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            data.append({"page": i, "text": text.strip()})
    return data
