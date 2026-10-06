import re
from enum import Enum

class Source(str, Enum):
    GENERAL = "general"
    WEBSITE = "website"
    SOURCE_TEXT = "source_text"

class Action(str, Enum):
    LEARN = "learn"
    QUIZ = "quiz"

class RequestType(str, Enum):
    GENERAL_LEARNING = "GENERAL_LEARNING"
    WEBSITE_LEARNING = "WEBSITE_LEARNING"
    SOURCE_TEXT_LEARNING = "SOURCE_TEXT_LEARNING"
    QUIZ = "QUIZ"

SOURCE_TEXT_MIN_CHARS = 1200
QUIZ_PATTERN = re.compile(r"\b(quiz|test me|practice questions?)\b", re.IGNORECASE)

def classify_query(
    query: str,
    has_url: bool,
    source_text: str | None = None,
) -> dict:
    """Choose the learning path without making an LLM call."""
    action = Action.QUIZ if QUIZ_PATTERN.search(query) else Action.LEARN

    if has_url:
        source = Source.WEBSITE
    elif (source_text and source_text.strip()) or len(query.strip()) >= SOURCE_TEXT_MIN_CHARS:
        source = Source.SOURCE_TEXT
    else:
        source = Source.GENERAL

    if action == Action.QUIZ:
        request_type = RequestType.QUIZ
    else:
        request_type = {
            Source.GENERAL: RequestType.GENERAL_LEARNING,
            Source.WEBSITE: RequestType.WEBSITE_LEARNING,
            Source.SOURCE_TEXT: RequestType.SOURCE_TEXT_LEARNING,
        }[source]

    return {
        "source": source,
        "action": action,
        "request_type": request_type,
    }