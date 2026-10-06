import re


def clean_topic_title(title: str) -> str:
    """Remove common Markdown formatting from a heading label."""
    title = re.sub(r"!?(?:\[([^\]]*)\])\([^)]+\)", r"\1", title)
    title = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", title)
    title = re.sub(r"(`+)(.+?)\1", r"\2", title)
    title = re.sub(r"(\*\*|__)(.+?)\1", r"\2", title)
    title = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", title)
    title = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", title)
    return " ".join(title.split()).strip()


def extract_topics(markdown: str) -> list[dict]:
    """
    Extract H1, H2 and H3 headings from Firecrawl markdown.
    """

    if not isinstance(markdown, str) or not markdown.strip():
        return []

    pattern = re.compile(
        r"^(#{1,3})\s+(.+)$",
        re.MULTILINE
    )

    topics = []

    for match in pattern.finditer(markdown):
        level = len(match.group(1))
        title = clean_topic_title(match.group(2))

        if not title:
            continue

        topics.append({
            "level": level,
            "title": title
        })

    return topics


def extract_section(markdown: str, topic_title: str) -> str:
    """Return a heading's content, including any nested subsections."""
    if not isinstance(markdown, str) or not topic_title:
        return ""

    pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    headings = list(pattern.finditer(markdown))

    for index, heading in enumerate(headings):
        heading_title = heading.group(2).strip()
        if (
            heading_title != topic_title
            and clean_topic_title(heading_title) != clean_topic_title(topic_title)
        ):
            continue

        level = len(heading.group(1))
        end = len(markdown)
        for next_heading in headings[index + 1:]:
            if len(next_heading.group(1)) <= level:
                end = next_heading.start()
                break

        return markdown[heading.end():end].strip()

    return ""