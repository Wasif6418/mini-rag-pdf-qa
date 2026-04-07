from __future__ import annotations

from dataclasses import dataclass

from rag.pdf_loader import PageText


@dataclass
class TextChunk:
    chunk_id: str
    page_number: int
    text: str


def split_into_chunks(
    pages: list[PageText],
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[TextChunk]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[TextChunk] = []

    for page in pages:
        text = page.text
        start = 0
        chunk_index = 1

        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_id=f"p{page.page_number}-c{chunk_index}",
                        page_number=page.page_number,
                        text=chunk_text,
                    )
                )

            if end >= len(text):
                break

            start = end - overlap
            chunk_index += 1

    return chunks
