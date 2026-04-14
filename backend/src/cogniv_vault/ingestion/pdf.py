"""PDF text extraction via pypdf."""

from __future__ import annotations

import io

from pypdf import PdfReader


def extract_text(file_bytes: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(file_bytes))
    page_count = len(reader.pages)
    if page_count == 0:
        raise ValueError("PDF has 0 pages")
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n\n".join(pages).strip(), page_count
