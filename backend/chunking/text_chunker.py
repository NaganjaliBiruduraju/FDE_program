from dataclasses import dataclass

from backend.parser.pdf_parser import ParsedDocument


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    page_number: int


def chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[TextChunk]:
    """Split text into overlapping fixed-size chunks."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    step = chunk_size - overlap
    start = 0
    chunk_number = 1

    while start < len(text):
        end = min(start + chunk_size, len(text))

        chunks.append(
            TextChunk(
                chunk_id=f"page_{page_number}_chunk_{chunk_number}",
                text=text[start:end],
                page_number=page_number,
            )
        )

        if end == len(text):
            break

        start += step
        chunk_number += 1

    return chunks