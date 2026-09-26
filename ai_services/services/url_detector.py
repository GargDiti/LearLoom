import re


def extract_url(text: str) -> str | None:
    pattern = r"https?://[^\s]+"
    match = re.search(pattern, text)
    if match:
        return match.group(0).rstrip(".,!?;:)]}")
    return None