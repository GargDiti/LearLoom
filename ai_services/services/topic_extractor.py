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
    """
    Extract the content belonging to a selected topic.
    """

    lines = markdown.splitlines()

    heading_pattern = re.compile(
        r"^(#{1,3})\s+(.+)$"
    )

    start_index = None
    topic_level = None

    # Find the selected topic
    for i, line in enumerate(lines):

        match = heading_pattern.match(line)

        if match:
            level = len(match.group(1))
            title = match.group(2).strip()

            if title == topic_title:
                start_index = i
                topic_level = level
                break

    # Topic wasn't found
    if start_index is None:
        return ""

    # Find where this topic ends
    end_index = len(lines)

    for i in range(start_index + 1, len(lines)):

        match = heading_pattern.match(lines[i])

        if match:
            level = len(match.group(1))

            # Same or higher-level heading means
            # the current section has ended.
            if level <= topic_level:
                end_index = i
                break

    return "\n".join(
        lines[start_index:end_index]
    ).strip()