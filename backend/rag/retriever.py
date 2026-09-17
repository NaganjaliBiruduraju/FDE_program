import re

from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore


class RAGRetriever:
    """Retrieve relevant chunks using semantic and keyword matching."""

    def __init__(
        self,
        persist_directory: str = "documents/vector_db",
        collection_name: str = "document_chunks",
    ):
        self.embedder = TextEmbedder()

        self.vector_store = ChromaVectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )

    def retrieve(
        self,
        query: str,
        file_name: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Retrieve relevant chunks using hybrid retrieval."""

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            raise ValueError("query cannot be empty")

        if not isinstance(file_name, str):
            raise TypeError("file_name must be a string")

        if not file_name.strip():
            raise ValueError("file_name cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        semantic_results = self._semantic_retrieve(
            query=query,
            file_name=file_name,
            top_k=top_k,
        )

        keyword_results = self._keyword_retrieve(
            query=query,
            file_name=file_name,
        )

        return self._combine_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            top_k=top_k,
        )

    def _semantic_retrieve(
        self,
        query: str,
        file_name: str,
        top_k: int,
    ) -> list[dict]:
        """Retrieve chunks using embedding similarity."""

        query_embedding = self.embedder.embed_text(query)

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "file_name": file_name,
            },
        )

        retrieved_chunks = []

        for i in range(len(results["ids"][0])):
            retrieved_chunks.append(
                {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "keyword_score": 0.0,
                }
            )

        return retrieved_chunks

    def _keyword_retrieve(
        self,
        query: str,
        file_name: str,
    ) -> list[dict]:
        """Retrieve chunks containing terms from the user query."""

        results = self.vector_store.collection.get(
            where={
                "file_name": file_name,
            },
            include=[
                "documents",
                "metadatas",
            ],
        )

        query_terms = self._tokenize(query)

        if not query_terms:
            return []

        keyword_results = []

        for i, text in enumerate(results["documents"]):
            text_lower = text.lower()
            matched_terms = sum(
                1
                for term in query_terms
                if term in text_lower
            )

            if matched_terms == 0:
                continue

            keyword_score = matched_terms / len(query_terms)

            keyword_results.append(
                {
                    "chunk_id": results["ids"][i],
                    "text": text,
                    "metadata": results["metadatas"][i],
                    "distance": None,
                    "keyword_score": keyword_score,
                }
            )

        keyword_results.sort(
            key=lambda result: result["keyword_score"],
            reverse=True,
        )

        return keyword_results

    def _combine_results(
        self,
        semantic_results: list[dict],
        keyword_results: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Combine semantic and keyword retrieval results."""

        combined = {}

        for rank, result in enumerate(semantic_results):
            combined[result["chunk_id"]] = {
                **result,
                "semantic_rank": rank + 1,
            }

        for rank, result in enumerate(keyword_results):
            chunk_id = result["chunk_id"]

            if chunk_id in combined:
                combined[chunk_id]["keyword_score"] = result[
                    "keyword_score"
                ]
            else:
                combined[chunk_id] = {
                    **result,
                    "semantic_rank": None,
                }

        def ranking_score(result):
            semantic_rank = result["semantic_rank"]

            semantic_score = (
                1 / semantic_rank
                if semantic_rank is not None
                else 0
            )

            keyword_score = result["keyword_score"]

            return (
                0.6 * semantic_score
                + 0.4 * keyword_score
            )

        ranked_results = sorted(
            combined.values(),
            key=ranking_score,
            reverse=True,
        )

        return ranked_results[:top_k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Convert text into searchable terms."""

        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )