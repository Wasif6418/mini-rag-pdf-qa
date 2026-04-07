from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass
class PageText:
    page_number: int
    text: str


def extract_pages(pdf_bytes: bytes) -> list[PageText]:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages: list[PageText] = []

    for index, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned_text = " ".join(raw_text.split())
        if cleaned_text:
            pages.append(PageText(page_number=index, text=cleaned_text))

    return pages
