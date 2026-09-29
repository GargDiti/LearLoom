import os
from groq import Groq

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