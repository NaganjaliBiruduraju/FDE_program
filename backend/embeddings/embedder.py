from sentence_transformers import SentenceTransformer


class TextEmbedder:
    """Generate embeddings for text."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            raise ValueError("text cannot be empty")

        embedding = self.model.encode(text)

        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not isinstance(texts, list):
            raise TypeError("texts must be a list")

        if not texts:
            return []

        if not all(isinstance(text, str) for text in texts):
            raise TypeError("every item in texts must be a string")

        if any(not text.strip() for text in texts):
            raise ValueError("texts cannot contain empty strings")

        embeddings = self.model.encode(texts)

        return embeddings.tolist()