import os
from pathlib import Path
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import asyncio
import hashlib
import json
import logging

from urllib.parse import urlsplit, urlunsplit

from services.redis_cache import (
    get_cached_value,
    set_cached_value,
)

logger = logging.getLogger(__name__)

FIRECRAWL_CACHE_TTL = 86400  # 24 hours
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FirecrawlApp(
    api_key=os.getenv("FIRECRAWL_API_KEY")
)



def make_firecrawl_cache_key(url: str) -> str:
    """Create a stable cache key for a webpage URL."""

    url = url.strip()
    parts = urlsplit(url)

    # Normalize scheme and hostname, and ignore URL fragments.
    normalized_url = urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path or "/",
        parts.query,
        "",
    ))

    key_hash = hashlib.sha256(
        normalized_url.encode("utf-8")
    ).hexdigest()

    return f"learnloom:firecrawl:{key_hash}"


async def scrape_page_with_cache(url: str) -> dict:
    """Reuse cached webpage content or scrape and cache it."""

    if not url.strip():
        raise ValueError("URL cannot be empty.")

    cache_key = make_firecrawl_cache_key(url)

    # 1. Look for previously scraped content.
    cached_data = await get_cached_value(cache_key)

    if (
        isinstance(cached_data, dict)
        and isinstance(cached_data.get("markdown"), str)
        and cached_data["markdown"].strip()
    ):
        logger.info("Firecrawl cache hit.")
        return cached_data

    # 2. Cache miss: run the existing scraper.
    logger.info("Firecrawl cache miss.")

    result = await asyncio.to_thread(scrape_page, url)

    # 3. Save only a successful, non-empty scrape.
    if (
        isinstance(result, dict)
        and isinstance(result.get("markdown"), str)
        and result["markdown"].strip()
    ):
        saved = await set_cached_value(
            cache_key,
            result,
            ttl_seconds=FIRECRAWL_CACHE_TTL,
        )

        if not saved:
            logger.warning("Could not save webpage in Redis cache.")

    return result
def scrape_page(url: str) -> dict:
    result = app.scrape_url(url, formats=["markdown"])
    if not isinstance(result, dict):
        result = result.model_dump()

    return {
        "url": url,
        "title": result.get("metadata", {}).get("title", ""),
        "markdown": result.get("markdown", "")
    }