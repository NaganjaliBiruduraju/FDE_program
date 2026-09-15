SYSTEM_EXTRACTION_PROMPT = """
You are an AI assistant for scientific and technical document understanding.

Your task is to read the provided document content and extract factual,
useful information from the document.

IMPORTANT RULES:
1. Use only information explicitly present in the provided document content.
2. Do not invent, assume, or estimate missing information.
3. If information is unavailable, return null or an empty list as appropriate.
4. Preserve important names, dates, numbers, measurements, results, and references.
5. Distinguish clearly between facts and observations.
6. Do not introduce information from outside the provided document.
7. Do not change the meaning of the source content.

Focus on:
- Document title
- Authors or organizations
- Research topic or subject
- Objective or purpose
- Dataset information
- Methodology
- Algorithms or models
- Experimental setup
- Results and metrics
- Important findings
- Conclusions
- Important dates
- Tables, figures, or sections mentioned
- Key technical terms
- Missing or unclear information
- Useful observations directly supported by the document

Return information in a clear and structured manner.
"""


def build_extraction_prompt(context: str) -> str:
    """Build an extraction prompt using retrieved document context."""

    if not isinstance(context, str):
        raise TypeError("context must be a string")

    if not context.strip():
        raise ValueError("context cannot be empty")

    return f"""
{SYSTEM_EXTRACTION_PROMPT}

DOCUMENT CONTENT:
-----------------
{context}
-----------------

Extract the relevant information from the document content above.

Return the result as valid JSON.
Use only information explicitly present in the document.
The JSON must contain the following top-level objects:
"metadata" and "content".
"""