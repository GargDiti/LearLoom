import json
from enum import Enum
from groq import Groq

client = Groq()

class Source(str, Enum):
    GENERAL = "general"
    WEBSITE = "website"

class Action(str, Enum):
    LEARN = "learn"
    QUIZ = "quiz"

CLASSIFY_PROMPT = """Classify the user's learning request along two independent dimensions.

SOURCE — where the learning material comes from:
- "general": no specific webpage involved, or user just names a topic
- "website": user references a specific webpage/URL to learn from or quiz on

ACTION — what the user wants done:
- "learn": user wants an explanation/teaching of a topic
- "quiz": user wants to be tested, quizzed, or given practice questions

Respond with ONLY valid JSON: {{"source": "<general|website>", "action": "<learn|quiz>"}}

User query: {query}
Has URL present: {has_url}
"""

def classify_query(query: str, has_url: bool) -> dict:
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": CLASSIFY_PROMPT.format(query=query, has_url=has_url)}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content)

    source_str = result.get("source", "general")
    action_str = result.get("action", "learn")

    # has_url is a hard signal from code — never let the LLM contradict it
    if has_url:
        source_str = "website"

    try:
        source = Source(source_str)
    except ValueError:
        source = Source.GENERAL

    try:
        action = Action(action_str)
    except ValueError:
        action = Action.LEARN

    return {"source": source, "action": action}