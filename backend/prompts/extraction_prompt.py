def build_extraction_prompt(
    user_prompt: str,
    context: str,
    prompt_requirements: dict,
) -> str:
    """Build a grounded LLM prompt using retrieved document context."""

    if not isinstance(user_prompt, str):
        raise TypeError("user_prompt must be a string")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    if not isinstance(context, str):
        raise TypeError("context must be a string")

    if not context.strip():
        raise ValueError("context cannot be empty")

    if not isinstance(prompt_requirements, dict):
        raise TypeError(
            "prompt_requirements must be a dictionary"
        )

    word_limit = prompt_requirements.get(
        "word_limit"
    )

    number_of_points = prompt_requirements.get(
        "number_of_points"
    )

    response_format = prompt_requirements.get(
        "response_format"
    )

    request_type = prompt_requirements.get(
        "request_type"
    )

    return f"""
You are a document-grounded AI assistant.

Your task is to answer the user's request using ONLY the
retrieved document context provided below.

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

RETRIEVED DOCUMENT CONTEXT:
============================
{context}
============================

GROUNDING RULES:

1. Treat the retrieved document context as the ONLY source of truth.

2. Use only facts, statements, definitions, numbers, names, and
   relationships explicitly supported by the retrieved context.

3. Do NOT use your general knowledge, training knowledge, assumptions,
   or external information to fill gaps.

4. Do NOT infer information that is not directly supported by the
   retrieved context.

5. If the context does not contain enough information to answer the
   request completely, clearly identify the missing information.

6. Never fabricate facts, examples, values, names, dates, or explanations.

7. When explaining a concept, stay within the terminology and meaning
   supported by the document.

8. If multiple parts of the context provide different information,
   report the conflict instead of silently choosing one.

9. Do not treat the user's question as evidence. The document context
   is the evidence.

10. Every factual statement in the answer must be supported by the
    retrieved document context.

11. Do not add commonly known information merely to make the answer
    longer or more complete.

12. Extract only information relevant to the user's request.

RESPONSE REQUIREMENTS:

13. Follow the requested response format.

14. If a word limit is specified, keep the answer reasonably close
    to that limit without adding unsupported information.

15. If a number of points is specified, provide exactly that number
    of points when enough relevant information exists.

16. If the requested number of points cannot be supported by the
    document, provide only supported information and explain what
    is missing.

17. Make the answer clear and meaningful while remaining grounded.

18. The "extracted_information" object must contain only information
    relevant to the user's request.

19. Do not create fixed fields such as research_topic, methodology,
    authors, dataset, or conclusions unless the user's request
    specifically asks for them.

20. The "sources" field will be populated by the application.
    Return it as an empty list.

Return valid JSON with exactly these top-level fields:

{{
    "answer": "A clear answer supported only by the document context.",
    "extracted_information": {{}},
    "missing_information": [],
    "sources": []
}}

Before producing the final answer, internally verify:

- Is every factual claim supported by the retrieved context?
- Did I introduce any outside knowledge?
- Did I infer anything unsupported?
- Did I follow the user's requested format and constraints?

If a fact is not supported by the retrieved context, leave it out
or identify it in "missing_information".
"""