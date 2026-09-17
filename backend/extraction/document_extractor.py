import json

from backend.llm.llm_service import GroqLLM
from backend.prompts.extraction_prompt import build_extraction_prompt
from backend.schemas.document_schema import DocumentResponse


class DocumentExtractor:
    """Generate a response from document context based on a user prompt."""

    def __init__(self):
        self.llm = GroqLLM()

    def extract(
        self,
        user_prompt: str,
        context: str,
    ) -> DocumentResponse:
        """Generate and validate a prompt-driven document response."""

        if not isinstance(user_prompt, str):
            raise TypeError("user_prompt must be a string")

        if not user_prompt.strip():
            raise ValueError("user_prompt cannot be empty")

        if not isinstance(context, str):
            raise TypeError("context must be a string")

        if not context.strip():
            raise ValueError("context cannot be empty")

        prompt = build_extraction_prompt(
            user_prompt=user_prompt,
            context=context,
        )

        response = self.llm.generate_json(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM response is not valid JSON"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "LLM response must be a JSON object"
            )

        data.setdefault("answer", "")
        data.setdefault("extracted_information", {})
        data.setdefault("missing_information", [])
        data.setdefault("sources", [])

        return DocumentResponse.model_validate(data)