import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def explain_topic(topic:str,content:str)->str:
    prompt = f"""
    You are an AI tutor.

    Teach the following topic to a student.

    Topic:
    {topic}

    Source content:
    {content}

    Instructions:
    - Explain the topic clearly and step by step.
    - you try first lisiting the topics present in the source and then explain them in detail.
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