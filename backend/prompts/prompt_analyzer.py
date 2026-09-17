import re


def analyze_prompt(user_prompt: str) -> dict:
    """Analyze a user prompt and identify response requirements."""

    if not isinstance(user_prompt, str):
        raise TypeError("user_prompt must be a string")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    prompt = user_prompt.strip()

    word_limit = None
    number_of_points = None

    word_match = re.search(
        r"\b(?:in|within|under|around|approximately)?\s*(\d+)\s*words?\b",
        prompt,
        re.IGNORECASE,
    )

    if word_match:
        word_limit = int(word_match.group(1))

    points_match = re.search(
        r"\b(\d+)\s*(?:points?|bullet\s*points?)\b",
        prompt,
        re.IGNORECASE,
    )

    if points_match:
        number_of_points = int(points_match.group(1))

    lower_prompt = prompt.lower()

    if "table" in lower_prompt:
        response_format = "table"
    elif number_of_points is not None:
        response_format = "points"
    elif any(
        word in lower_prompt
        for word in ["list", "enumerate", "bullet"]
    ):
        response_format = "list"
    else:
        response_format = "paragraph"

    if any(
        word in lower_prompt
        for word in ["summarize", "summary", "summarise"]
    ):
        request_type = "summary"
    elif any(
        word in lower_prompt
        for word in ["compare", "comparison", "difference", "differences"]
    ):
        request_type = "comparison"
    elif any(
        word in lower_prompt
        for word in ["explain", "describe", "what is", "what are"]
    ):
        request_type = "explanation"
    else:
        request_type = "general"

    return {
        "original_prompt": prompt,
        "word_limit": word_limit,
        "number_of_points": number_of_points,
        "response_format": response_format,
        "request_type": request_type,
    }