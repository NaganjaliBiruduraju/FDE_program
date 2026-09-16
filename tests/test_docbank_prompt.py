from backend.parser.pdf_parser import parse_pdf
from backend.preprocessing.text_cleaner import preprocess_document
from backend.chunking.text_chunker import chunk_document
from backend.embeddings.embedder import TextEmbedder
from backend.vector_store.chroma_store import ChromaVectorStore
from backend.rag.retriever import RAGRetriever
from backend.prompts.extraction_prompt import build_extraction_prompt

pdf_path = r"data/raw/pdf/10.tar_1701.04170.gz_TPNL_afterglow_evo_black.pdf"

document = parse_pdf(pdf_path)
document = preprocess_document(document)
chunks = chunk_document(document)

embedder = TextEmbedder()
embeddings = embedder.embed_texts(
    [chunk.text for chunk in chunks[:5]]
)

store = ChromaVectorStore(
    persist_directory="documents/docbank_test_vector_db",
    collection_name="docbank_test_chunks",
)

store.add_chunks(chunks[:5], embeddings)

retriever = RAGRetriever(
    persist_directory="documents/docbank_test_vector_db",
    collection_name="docbank_test_chunks",
)

results = retriever.retrieve(
    "What is this document about?",
    top_k=3,
)

context = "\n\n".join(
    result["text"] for result in results
)

prompt = build_extraction_prompt(context)

print("Retrieved chunks:", len(results))
print("Context length:", len(context))
print("Prompt length:", len(prompt))
print("PASS:", len(results) == 3 and len(context) > 0 and len(prompt) > 0)
