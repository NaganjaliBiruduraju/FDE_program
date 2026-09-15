import numpy as np
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


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not vector_a or not vector_b:
        raise ValueError("vectors cannot be empty")

    if len(vector_a) != len(vector_b):
        raise ValueError("vectors must have the same dimensions")

    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        raise ValueError("vectors cannot have zero magnitude")

    return float(np.dot(a, b) / denominator)