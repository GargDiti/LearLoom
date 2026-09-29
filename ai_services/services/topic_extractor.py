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


def extract_section(markdown: str, topic_title: str) -> str:
    """Return a heading's content, including any nested subsections."""
    pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    headings = list(pattern.finditer(markdown))

    for index, heading in enumerate(headings):
        if heading.group(2).strip() != topic_title:
            continue

        level = len(heading.group(1))
        end = len(markdown)
        for next_heading in headings[index + 1:]:
            if len(next_heading.group(1)) <= level:
                end = next_heading.start()
                break

        return markdown[heading.end():end].strip()

    return ""