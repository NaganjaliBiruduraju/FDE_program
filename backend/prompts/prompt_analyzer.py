import re


def analyze_prompt(user_prompt: str) -> dict:
    """Analyze a user prompt and identify response requirements."""

    if not isinstance(user_prompt, str):
        raise TypeError("user_prompt must be a string")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    prompt = user_prompt.strip()
    lower_prompt = prompt.lower()

    word_limit = _extract_word_limit(prompt)
    number_of_points = _extract_number_of_points(prompt)
    response_format = _detect_response_format(
        lower_prompt,
        number_of_points,
    )
    request_type = _detect_request_type(lower_prompt)

    prompt_quality = _assess_prompt_quality(
        prompt=prompt,
        request_type=request_type,
    )

    return {
        "original_prompt": prompt,
        "word_limit": word_limit,
        "number_of_points": number_of_points,
        "response_format": response_format,
        "request_type": request_type,
        "prompt_quality": prompt_quality,
    }


def _extract_word_limit(
    prompt: str,
) -> int | None:
    """Extract a requested word limit."""

    word_match = re.search(
        r"\b(?:in|within|under|around|approximately)?\s*(\d+)\s*words?\b",
        prompt,
        re.IGNORECASE,
    )

    if word_match:
        return int(word_match.group(1))

    return None


def _extract_number_of_points(
    prompt: str,
) -> int | None:
    """Extract a requested number of points."""

    points_match = re.search(
        r"\b(\d+)\s*(?:points?|bullet\s*points?)\b",
        prompt,
        re.IGNORECASE,
    )

    if points_match:
        return int(points_match.group(1))

    return None


def _detect_response_format(
    lower_prompt: str,
    number_of_points: int | None,
) -> str:
    """Detect the requested response format."""

    if "table" in lower_prompt:
        return "table"

    if number_of_points is not None:
        return "points"

    if any(
        word in lower_prompt
        for word in [
            "list",
            "enumerate",
            "bullet",
        ]
    ):
        return "list"

    return "paragraph"


def _detect_request_type(
    lower_prompt: str,
) -> str:
    """Detect the main type of user request."""

    if any(
        word in lower_prompt
        for word in [
            "summarize",
            "summary",
            "summarise",
        ]
    ):
        return "summary"

    if any(
        word in lower_prompt
        for word in [
            "compare",
            "comparison",
            "difference",
            "differences",
        ]
    ):
        return "comparison"

    if any(
        word in lower_prompt
        for word in [
            "explain",
            "describe",
            "what is",
            "what are",
            "how does",
            "how do",
            "why",
        ]
    ):
        return "explanation"

    return "general"


def _assess_prompt_quality(
    prompt: str,
    request_type: str,
) -> dict:
    """Assess whether the prompt provides enough information."""

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        prompt.lower(),
    )

    meaningful_words = [
        word
        for word in words
        if word not in {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "what",
            "why",
            "how",
            "does",
            "do",
            "can",
            "could",
            "would",
            "should",
            "please",
            "tell",
            "me",
            "about",
            "this",
            "that",
            "it",
        }
    ]

    if len(meaningful_words) == 0:
        return {
            "status": "weak",
            "reason": "The prompt does not specify what information is needed.",
        }

    if len(meaningful_words) == 1:
        return {
            "status": "weak",
            "reason": "The prompt contains only a topic and does not specify what to do with it.",
        }

    if request_type == "general" and len(meaningful_words) <= 2:
        return {
            "status": "weak",
            "reason": "The prompt provides a topic but does not clearly specify the requested task.",
        }

    return {
        "status": "sufficient",
        "reason": None,
    }