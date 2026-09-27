import re


def extract_topics(markdown: str) -> list[dict]:
    """
    Extract H1, H2 and H3 headings from Firecrawl markdown.
    """

    pattern = re.compile(
        r"^(#{1,3})\s+(.+)$",
        re.MULTILINE
    )

    topics = []

    for match in pattern.finditer(markdown):
        level = len(match.group(1))
        title = match.group(2).strip()

        topics.append({
            "level": level,
            "title": title
        })

    return topics