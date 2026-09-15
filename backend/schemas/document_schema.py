from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Basic metadata about the document."""

    file_name: str
    document_title: str | None = None
    authors: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)


class DocumentContent(BaseModel):
    """Structured information extracted from the document."""

    research_topic: str | None = None
    objective: str | None = None
    dataset_information: str | None = None
    methodology: str | None = None
    algorithms_or_models: list[str] = Field(default_factory=list)
    experimental_setup: str | None = None
    results_and_metrics: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    conclusions: str | None = None
    important_dates: list[str] = Field(default_factory=list)
    technical_terms: list[str] = Field(default_factory=list)
    missing_or_unclear_information: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)


class StructuredDocument(BaseModel):
    """Complete structured representation of a document."""

    metadata: DocumentMetadata
    content: DocumentContent
    