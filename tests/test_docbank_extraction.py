from backend.parser.pdf_parser import parse_pdf
from backend.preprocessing.text_cleaner import preprocess_document
from backend.chunking.text_chunker import chunk_document
from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore
from backend.rag.retriever import RAGRetriever
from backend.extraction.document_extractor import DocumentExtractor

pdf_path = r"data/raw/pdf/10.tar_1701.04170.gz_TPNL_afterglow_evo_black.pdf"

document = parse_pdf(pdf_path)
document = preprocess_document(document)
chunks = chunk_document(document)

embedder = TextEmbedder()

test_chunks = chunks[:10]

embeddings = embedder.embed_texts(
    [chunk.text for chunk in test_chunks]
)

store = ChromaVectorStore(
    persist_directory="documents/docbank_real_vector_db",
    collection_name="docbank_real_chunks",
)

if store.count() == 0:
    store.add_chunks(test_chunks, embeddings)

retriever = RAGRetriever(
    persist_directory="documents/docbank_real_vector_db",
    collection_name="docbank_real_chunks",
)

results = retriever.retrieve(
    "What is the research topic, methodology, and main findings of this document?",
    top_k=5,
)

context = "\n\n".join(
    result["text"] for result in results
)

extractor = DocumentExtractor()

result = extractor.extract(
    context=context,
    file_name=document.file_name,
)

print("Real DocBank extraction: PASS")
print("File:", result.metadata.file_name)
print("Title:", result.metadata.document_title)
print("Research topic:", result.content.research_topic)
print("Objective:", result.content.objective)
print("Methodology:", result.content.methodology)
print("Key findings:", result.content.key_findings)
print("PASS:", result.metadata.file_name == document.file_name)
