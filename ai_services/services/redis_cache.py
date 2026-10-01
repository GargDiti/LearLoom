
import json
import logging
import os
from dotenv import load_dotenv
from upstash_redis.asyncio import Redis
import hashlib

load_dotenv()
logger = logging.getLogger(__name__)
redis_client = Redis.from_env()


async def get_cached_value(key: str):
    """Return a cached JSON value, or None if it is missing."""
    try:
        value = await redis_client.get(key)

        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        if isinstance(value, str):
            return json.loads(value)

        return value

    except Exception:
        logger.exception("Redis cache read failed")
        return None


async def set_cached_value(
    key: str,
    value,
    ttl_seconds: int = 604800,
):
    """Save a JSON-compatible value for a limited time."""
    if ttl_seconds <= 0:
        raise ValueError("TTL must be greater than zero")

    try:
        serialized_value = json.dumps(value, ensure_ascii=False)

        await redis_client.set(
            key,
            serialized_value,
            ex=ttl_seconds,
        )

        return True

    except Exception:
        logger.exception("Redis cache write failed")
        return False


async def delete_cached_value(key: str):
    """Delete a cached value."""
    try:
        await redis_client.delete(key)
        return True

    except Exception:
        logger.exception("Redis cache delete failed")
        return False


async def check_redis_connection():
    """Check whether Redis is reachable."""
    try:
        result = await redis_client.ping()
        return bool(result)

    except Exception:
        logger.exception("Redis health check failed")
        return False

def create_cache_key(
    question: str,
    source_content: str = "",
    model: str = "llama-3.1-8b-instant",
    prompt_version: str = "v1",
) -> str:
    """Create a stable key for equivalent learning requests."""

    normalized_question = " ".join(question.strip().lower().split())

    content_hash = hashlib.sha256(
        source_content.encode("utf-8")
    ).hexdigest()

    key_data = {
        "question": normalized_question,
        "content_hash": content_hash,
        "model": model,
        "prompt_version": prompt_version,
    }

    serialized = json.dumps(
        key_data,
        sort_keys=True,
        ensure_ascii=False,
    )

    request_hash = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return f"learnloom:explanation:{request_hash}"