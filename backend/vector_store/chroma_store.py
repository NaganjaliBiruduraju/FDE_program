import chromadb


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