from pathlib import Path

from backend.parser.pdf_parser import parse_pdf
from backend.preprocessing.text_cleaner import preprocess_document
from backend.chunking.text_chunker import chunk_document
from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore
from backend.rag.retriever import RAGRetriever
from backend.extraction.document_extractor import DocumentExtractor
from backend.evaluation.evaluator import DocumentEvaluator


class DocumentPipeline:
    """Run the complete document processing pipeline."""

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
        self.evaluator = DocumentEvaluator()

    def process(
        self,
        pdf_path: str | Path,
        query: str,
        top_k: int = 5,
    ) -> dict:
        """Process a PDF and return structured extraction with evaluation."""

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file: {pdf_path}")

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            raise ValueError("query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        # 1. Parse PDF
        document = parse_pdf(pdf_path)

        # 2. Preprocess text
        document = preprocess_document(document)

        # 3. Create chunks
        chunks = chunk_document(document)

        if not chunks:
            raise ValueError("No text chunks were created from the document")

        # 4. Generate embeddings
        embeddings = self.embedder.embed_texts(
            [chunk.text for chunk in chunks]
        )

        # 5. Store chunks and embeddings
        self.vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        # 6. Retrieve relevant chunks
        retriever = RAGRetriever(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )

        results = retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        # 7. Build context
        context = "\n\n".join(
            result["text"]
            for result in results
        )

        # 8. Extract structured information
        structured_document = self.extractor.extract(
            context=context,
            file_name=document.file_name,
        )

        # 9. Evaluate extraction
        evaluation = self.evaluator.evaluate(
            structured_document
        )

        return {
            "document": structured_document,
            "evaluation": evaluation,
            "retrieved_chunks": results,
        }