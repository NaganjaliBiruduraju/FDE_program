from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """Basic metadata about the document."""

    file_name: str
    document_title: str | None = None
    authors: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)

    @field_validator("authors", "organizations", mode="before")
    @classmethod
    def normalize_lists(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, dict):
            return [
                f"{key}: {item}"
                for key, item in value.items()
            ]

        return value


class DocumentContent(BaseModel):
    """Structured information extracted from the document."""

    research_topic: str | None = None
    objective: str | None = None
    dataset_information: str | None = None
    methodology: list[str] = Field(default_factory=list)
    algorithms_or_models: list[str] = Field(default_factory=list)
    experimental_setup: str | None = None
    results_and_metrics: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    conclusions: str | None = None
    important_dates: list[str] = Field(default_factory=list)
    technical_terms: list[str] = Field(default_factory=list)
    missing_or_unclear_information: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)

    @field_validator(
        "algorithms_or_models",
        "methodology",
        "results_and_metrics",
        "key_findings",
        "important_dates",
        "technical_terms",
        "missing_or_unclear_information",
        "observations",
        mode="before",
    )
    @classmethod
    def normalize_lists(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, dict):
            return [
                f"{key}: {item}"
                for key, item in value.items()
            ]

        return value

    @field_validator("dataset_information", mode="before")
    @classmethod
    def normalize_dataset_information(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            return "; ".join(
                f"{key}: {item}"
                for key, item in value.items()
            )

        return str(value)


class StructuredDocument(BaseModel):
    """Complete structured representation of a document."""

    metadata: DocumentMetadata
    content: DocumentContent