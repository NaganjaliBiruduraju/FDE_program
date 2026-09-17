from typing import Any

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Reference to the document content used for the response."""

    file_name: str
    page_number: int


class DocumentResponse(BaseModel):
    """Flexible response generated from a document and user prompt."""

    answer: str
    extracted_information: dict[str, Any] = Field(
        default_factory=dict
    )
    missing_information: list[str] = Field(
        default_factory=list
    )
    sources: list[SourceReference] = Field(
        default_factory=list
    )