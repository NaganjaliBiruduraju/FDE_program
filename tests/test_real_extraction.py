from backend.extraction.document_extractor import DocumentExtractor

extractor = DocumentExtractor()

context = """
This scientific paper presents a study of a physical phenomenon.
The authors investigate the evolution of the observed system using
numerical modeling and observational data.

The study uses a computational model to analyze the behavior of the system.
The results show that the model reproduces several observed characteristics.
The authors conclude that the proposed approach provides useful insight
into the evolution of the system.
"""

result = extractor.extract(
    context=context,
    file_name="docbank_real_test.pdf",
)

print("Extraction: PASS")
print("File:", result.metadata.file_name)
print("Title:", result.metadata.document_title)
print("Topic:", result.content.research_topic)
print("Objective:", result.content.objective)
print("Methodology:", result.content.methodology)
print("Findings:", result.content.key_findings)
print("PASS:", result.metadata.file_name == "docbank_real_test.pdf")
