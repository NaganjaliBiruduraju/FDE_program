from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore


class RAGRetriever:
    """Retrieve relevant chunks from a specific document."""

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
        """Retrieve relevant chunks from the specified document."""

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
                }
            )

        return retrieved_chunks