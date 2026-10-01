import os
from groq import Groq
from services.redis_cache import (
    get_cached_value,
    set_cached_value,
    create_cache_key,
)

MODEL_NAME = "qwen/qwen3.8-27b"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def explain_topic(topic: str, content: str) -> str:

    prompt = f"""
You are an AI tutor.

Teach the following topic to a student.

Topic:
{topic}

Source content:
{content}

Instructions:
- Explain the topic clearly and step by step.
- Use the provided source content as the primary basis.
- Do not unnecessarily introduce unrelated information.
- Use examples where they help understanding.
- Assume the student is learning this topic for the first time.
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def explain_general_query(query: str) -> str:
    """
    Explain a user's learning query without requiring a URL.
    """

    if not query.strip():
        raise ValueError("Learning query cannot be empty.")

    prompt = f"""
You are LearnLoom, a friendly AI tutor.

The student wants to learn the following topic:
{query}

Your task:
1. Explain the concept in beginner-friendly language.
2. Start with the fundamentals.
3. Organize the answer using headings and bullet points.
4. Explain important terms step by step.
5. Include examples wherever useful.
6. Mention important formulas or applications when relevant.
7. End with a short summary of the key points.

Do not assume the student has prior knowledge.
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": "You are a patient tutor who teaches concepts clearly."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content or ""

