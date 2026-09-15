from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class PageContent:
    page_number: int
    text: str


@dataclass
class ParsedDocument:
    file_name: str
    page_count: int
    pages: list[PageContent]


def parse_pdf(pdf_path: str | Path) -> ParsedDocument:
    """Extract text from a PDF page by page."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {pdf_path}")

    try:
        document = pymupdf.open(pdf_path)
    except Exception as exc:
        raise ValueError(f"Unable to open PDF: {pdf_path}") from exc

    try:
        pages = []

        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()

            pages.append(
                PageContent(
                    page_number=page_number,
                    text=text,
                )
            )

        return ParsedDocument(
            file_name=pdf_path.name,
            page_count=len(document),
            pages=pages,
        )

    finally:
        document.close()