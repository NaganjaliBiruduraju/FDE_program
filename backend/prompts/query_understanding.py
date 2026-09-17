import re


STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "in", "on", "of",
    "to", "for", "and", "or", "how", "does", "do", "why",
    "can", "could", "would", "should", "please", "explain",
    "describe", "summarize", "summarise", "summary", "compare",
    "comparison", "difference", "differences", "give", "me",
    "list", "find", "extract", "from", "document", "documents",
    "words", "word", "points", "point", "table", "within",
    "under", "around", "approximately",
}


SECTION_NAMES = {
    "abstract",
    "introduction",
    "methodology",
    "method",
    "results",
    "discussion",
    "conclusion",
    "references",
}


def understand_query(user_prompt: str) -> dict:
    """Identify intent, concepts, keywords, and section hints."""

    if not isinstance(user_prompt, str):
        raise TypeError("user_prompt must be a string")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    prompt = user_prompt.strip()
    lower_prompt = prompt.lower()

    intent = _detect_intent(lower_prompt)

    section_hint = _detect_section(lower_prompt)

    quoted_terms = _extract_quoted_terms(prompt)

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9-]*\b",
        lower_prompt,
    )

    meaningful_words = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
        and not word.isdigit()
    ]

    concepts = _detect_concepts(
        meaningful_words=meaningful_words,
        prompt=lower_prompt,
    )

    keywords = []

    # Explicitly quoted terms are important.
    for term in quoted_terms:
        if term not in keywords:
            keywords.append(term)

    # Meaningful multi-word concepts are important.
    for concept in concepts:
        if concept not in keywords:
            keywords.append(concept)

    # Individual words remain useful as secondary signals.
    for word in meaningful_words:
        if word not in keywords:
            keywords.append(word)

    if concepts:
        primary_topic = _select_primary_concept(
            concepts
        )
    elif meaningful_words:
        primary_topic = meaningful_words[0]
    else:
        primary_topic = None

    secondary_topics = [
        concept
        for concept in concepts
        if concept != primary_topic
    ]

    important_terms = []

    if primary_topic:
        important_terms.append(primary_topic)

    for concept in secondary_topics:
        if concept not in important_terms:
            important_terms.append(concept)

    return {
        "intent": intent,
        "primary_topic": primary_topic,
        "secondary_topics": secondary_topics,
        "keywords": keywords,
        "important_terms": important_terms,
        "concepts": concepts,
        "section_hint": section_hint,
    }


def _detect_intent(prompt: str) -> str:
    """Detect the primary user intent."""

    if any(
        phrase in prompt
        for phrase in [
            "compare",
            "comparison",
            "difference",
            "differences",
        ]
    ):
        return "comparison"

    if any(
        phrase in prompt
        for phrase in [
            "summarize",
            "summarise",
            "summary",
        ]
    ):
        return "summary"

    if any(
        phrase in prompt
        for phrase in [
            "extract",
            "give me",
            "list",
            "find",
        ]
    ):
        return "information_extraction"

    if any(
        phrase in prompt
        for phrase in [
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

    return "question_answering"


def _detect_section(prompt: str) -> str | None:
    """Detect a document section mentioned by the user."""

    for section in SECTION_NAMES:
        if re.search(
            rf"\b{re.escape(section)}\b",
            prompt,
        ):
            return section

    return None


def _extract_quoted_terms(prompt: str) -> list[str]:
    """Extract explicitly quoted concepts."""

    matches = re.findall(
        r'"([^"]+)"|\'([^\']+)\'',
        prompt,
    )

    terms = []

    for first, second in matches:
        term = (first or second).strip().lower()

        if term:
            terms.append(term)

    return terms


def _detect_concepts(
    meaningful_words: list[str],
    prompt: str,
    ) -> list[str]:
    """Detect meaningful two-word concepts."""

    concepts = []

    concept_suffixes = {
        "tracker",
        "server",
        "system",
        "model",
        "manager",
        "controller",
        "engine",
        "framework",
        "algorithm",
        "architecture",
        "protocol",
        "database",
        "network",
        "service",
        "storage",
    }

    for index in range(len(meaningful_words) - 1):
        first = meaningful_words[index]
        second = meaningful_words[index + 1]

        if second in concept_suffixes:
            concept = f"{first} {second}"

            if concept not in concepts:
                concepts.append(concept)

    return concepts


def _is_likely_concept(words: list[str]) -> bool:
    """Check whether a phrase looks like a named concept."""

    concept_indicators = {
        "tracker",
        "server",
        "system",
        "model",
        "network",
        "database",
        "learning",
        "machine",
        "cloud",
        "data",
        "management",
        "processing",
        "architecture",
        "algorithm",
        "framework",
        "method",
        "function",
        "protocol",
        "storage",
        "engine",
        "service",
        "controller",
        "manager",
    }

    return any(
        word in concept_indicators
        for word in words
    )
def _select_primary_concept(
    concepts: list[str],
) -> str:
    """Select the strongest multi-word concept."""

    concept_indicators = {
        "tracker",
        "server",
        "system",
        "model",
        "architecture",
        "algorithm",
        "framework",
        "database",
        "network",
        "protocol",
        "manager",
        "controller",
        "service",
        "engine",
        "storage",
        "processing",
        "management",
        "learning",
        "method",
        "function",
    }

    def score(concept: str) -> int:
        return sum(
            1
            for word in concept.split()
            if word in concept_indicators
        )

    return max(
        concepts,
        key=score,
    )

    def score(concept: str) -> tuple[int, int]:
        words = concept.split()

        indicator_score = max(
            (
                concept_priority.get(word, 0)
                for word in words
            ),
            default=0,
        )

        # Prefer shorter concepts when the indicator
        # strength is the same.
        return (
            indicator_score,
            -len(words),
        )

    return max(
        concepts,
        key=score,
    )
