def build_extraction_prompt(
    user_prompt: str,
    context: str,
    prompt_requirements: dict,
) -> str:
    """Build an LLM prompt using the user's request and response requirements."""

    if not isinstance(user_prompt, str):
        raise TypeError("user_prompt must be a string")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    if not isinstance(context, str):
        raise TypeError("context must be a string")

    if not context.strip():
        raise ValueError("context cannot be empty")

    if not isinstance(prompt_requirements, dict):
        raise TypeError("prompt_requirements must be a dictionary")

    word_limit = prompt_requirements.get("word_limit")
    number_of_points = prompt_requirements.get("number_of_points")
    response_format = prompt_requirements.get("response_format")
    request_type = prompt_requirements.get("request_type")

    return f"""
You are an AI assistant that answers questions and extracts information
from documents.

The user has provided a document and a request.

USER REQUEST:
-----------------
{user_prompt}
-----------------

REQUEST TYPE:
{request_type}

RESPONSE FORMAT:
{response_format}

WORD LIMIT:
{word_limit}

NUMBER OF POINTS:
{number_of_points}

DOCUMENT CONTENT:
-----------------
{context}
-----------------

Follow these rules:

1. Answer the user's request using only the provided document content.
2. Extract only information relevant to the user's request.
3. Do not invent, assume, estimate, or add information that is not present.
4. If the requested information is not available in the document, clearly
   mention it in "missing_information".
5. Make the "answer" meaningful, clear, and easy to understand.
6. Preserve important names, dates, numbers, measurements, and facts exactly
   when they are available.
7. Follow the requested response format.
8. If a word limit is specified, keep the answer close to that word limit.
9. If a number of points is specified, provide exactly that number of points
   when the document contains enough relevant information.
10. If the requested format cannot be followed because the document does not
    contain enough information, clearly state what is missing.
11. If the document contains conflicting information, mention the conflict
    instead of choosing one without evidence.
12. Do not use outside knowledge.
13. The user's request determines what information should be extracted.

Return valid JSON with exactly these top-level fields:

{{
    "answer": "A clear and meaningful answer to the user's request.",
    "extracted_information": {{}},
    "missing_information": [],
    "sources": []
}}

The "extracted_information" object must be dynamic and contain only fields
relevant to the user's request.

Do not create fixed fields such as research_topic, methodology, authors,
dataset, or conclusions unless the user's request specifically asks for them.

The "sources" field will be populated by the application, so return it as
an empty list.
"""