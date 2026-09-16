from backend.extraction.document_extractor import DocumentExtractor

extractor = DocumentExtractor()

extractor.llm.generate = lambda prompt: """
{
    "metadata": {
        "file_name": "temporary.pdf",
        "document_title": "Test Research Paper",
        "authors": ["Author One"],
        "organizations": ["Research Organization"]
    },
    "content": {
        "research_topic": "Machine learning",
        "objective": "Evaluate a machine learning method",
        "dataset_information": "Experimental dataset",
        "methodology": "Model training and evaluation",
        "algorithms_or_models": ["Model A"],
        "experimental_setup": "Test environment",
        "results_and_metrics": ["Accuracy: 96.4%"],
        "key_findings": ["The model achieved high accuracy"],
        "conclusions": "The approach produced useful results",
        "important_dates": [],
        "technical_terms": ["machine learning"],
        "missing_or_unclear_information": [],
        "observations": ["The document reports experimental results"]
    }
}
"""

result = extractor.extract(
    context="This is test scientific document content.",
    file_name="docbank_test.pdf",
)

print("Extraction: PASS")
print("File:", result.metadata.file_name)
print("Title:", result.metadata.document_title)
print("Topic:", result.content.research_topic)
print("PASS:", result.metadata.file_name == "docbank_test.pdf")
