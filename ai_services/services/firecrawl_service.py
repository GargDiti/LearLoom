import os
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FirecrawlApp(
    api_key=os.getenv("FIRECRAWL_API_KEY")
)


def scrape_page(url: str) -> dict:
    result = app.scrape_url(url, formats=["markdown"])
    if not isinstance(result, dict):
        result = result.model_dump()

    return {
        "url": url,
        "title": result.get("metadata", {}).get("title", ""),
        "markdown": result.get("markdown", "")
    }