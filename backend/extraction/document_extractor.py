import json

from backend.llm.llm_service import GroqLLM
from backend.prompts.extraction_prompt import build_extraction_prompt
from backend.schemas.document_schema import StructuredDocument


class DocumentExtractor:
    """Extract structured information from document context using an LLM."""

    def __init__(self):
        self.llm = GroqLLM()

    def extract(self, context: str, file_name: str) -> StructuredDocument:
        """Generate and validate structured document information."""

        if not isinstance(context, str):
            raise TypeError("context must be a string")

        if not context.strip():
            raise ValueError("context cannot be empty")

        if not isinstance(file_name, str):
            raise TypeError("file_name must be a string")

        if not file_name.strip():
            raise ValueError("file_name cannot be empty")

        prompt = build_extraction_prompt(context)

        response = self.llm.generate_json(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response is not valid JSON") from exc

        if "metadata" not in data:
            data["metadata"] = {}

        data["metadata"]["file_name"] = file_name

        return StructuredDocument.model_validate(data)