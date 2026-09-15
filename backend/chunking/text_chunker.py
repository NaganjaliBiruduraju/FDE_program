from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    page_number: int