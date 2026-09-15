import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqLLM:
    """Service for interacting with the Groq LLM."""

    def __init__(
        self,
        model: str = "openai/gpt-oss-120b",
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate a text response from the Groq LLM."""

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content

    def generate_json(self, prompt: str) -> str:
        """Generate a JSON response from the Groq LLM."""

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content