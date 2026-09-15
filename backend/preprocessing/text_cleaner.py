import re


def clean_text(text: str) -> str:
    """Clean extracted PDF text while preserving meaningful content."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        # Replace tabs with spaces
        line = line.replace("\t", " ")

        # Collapse repeated spaces
        line = re.sub(r" {2,}", " ", line)

        # Remove leading/trailing spaces
        line = line.strip()

        lines.append(line)

    # Remove whitespace-only lines at the beginning/end
    # and collapse excessive blank lines
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()