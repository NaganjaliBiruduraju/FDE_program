from pathlib import Path

from backend.parser.pdf_parser import parse_pdf
from backend.preprocessing.text_cleaner import preprocess_document
from backend.chunking.text_chunker import chunk_document
from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore
from backend.rag.retriever import RAGRetriever
from backend.extraction.document_extractor import DocumentExtractor


class DocumentPipeline:
    """Run the complete prompt-driven document processing pipeline."""

    def __init__(
        self,
        persist_directory: str = "documents/pipeline_vector_db",
        collection_name: str = "pipeline_chunks",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.embedder = TextEmbedder()

        self.vector_store = ChromaVectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )

        self.extractor = DocumentExtractor()

        self.retriever = RAGRetriever(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )

    def process(
        self,
        pdf_path: str | Path,
        user_prompt: str,
        top_k: int = 5,
    ) -> dict:
        """Process a PDF according to the user's prompt."""

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file: {pdf_path}"
            )

        if not isinstance(user_prompt, str):
            raise TypeError(
                "user_prompt must be a string"
            )

        if not user_prompt.strip():
            raise ValueError(
                "user_prompt cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        # 1. Parse the PDF
        document = parse_pdf(pdf_path)

        # 2. Preprocess extracted text
        document = preprocess_document(document)

        # 3. Create document chunks
        chunks = chunk_document(document)

        if not chunks:
            raise ValueError(
                "No text chunks were created from the document"
            )

        # 4. Generate embeddings
        embeddings = self.embedder.embed_texts(
            [chunk.text for chunk in chunks]
        )

        # 5. Store chunks and embeddings
        self.vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        # 6. Retrieve relevant chunks using RAG
        results = self.retriever.retrieve(
            query=user_prompt,
            file_name=document.file_name,
            top_k=top_k,
        )

        if not results:
            raise ValueError(
                "No relevant information was found in the document"
            )

        # 7. Build context for the LLM
        context = "\n\n".join(
            result["text"]
            for result in results
        )

        # 8. Generate the prompt-driven response
        response = self.extractor.extract(
            user_prompt=user_prompt,
            context=context,
        )

        # 9. Create unique source references
        unique_sources = []
        seen_sources = set()

        for result in results:
            file_name = result["metadata"]["file_name"]
            page_number = result["metadata"]["page_number"]

            source_key = (
                file_name,
                page_number,
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            unique_sources.append(
                {
                    "file_name": file_name,
                    "page_number": page_number,
                }
            )

        response.sources = unique_sources

        return {
            "document": response,
            "retrieved_chunks": results,
        }