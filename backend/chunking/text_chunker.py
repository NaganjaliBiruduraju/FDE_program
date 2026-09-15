from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    page_number: int


def chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = 1000,
) -> list[TextChunk]:
    """Split text into fixed-size chunks."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    text = text.strip()

    if not text:
        return []

    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk_text_value = text[start:start + chunk_size]

        chunks.append(
            TextChunk(
                chunk_id=f"page_{page_number}_chunk_{len(chunks) + 1}",
                text=chunk_text_value,
                page_number=page_number,
            )
        )

    return chunks
