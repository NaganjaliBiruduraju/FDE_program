import chromadb

from backend.chunking.text_chunker import TextChunk


class ChromaVectorStore:
    """Manage the ChromaDB vector collection."""

    def __init__(
        self,
        persist_directory: str = "documents/vector_db",
        collection_name: str = "document_chunks",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def count(self) -> int:
        """Return the number of stored documents."""

        return self.collection.count()

    def add_chunks(
        self,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store text chunks and their embeddings."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        if not chunks:
            return

        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "file_name": chunk.file_name,
                    "page_number": chunk.page_number,
                }
                for chunk in chunks
            ],
        )