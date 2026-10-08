from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().with_name(".env"))
from services.url_detector import extract_url
from services.query_router import classify_query
from services.handlers import dispatch, prepare_website_learning

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    query: str
    source_text: str | None = None
    source_url: str | None = None
    selected_topic: str | None = None
    conversation_history: list[dict[str, str]] = Field(default_factory=list)

@app.post("/analyze-query")
def analyze_query(request: QueryRequest):
    url = extract_url(request.query) or request.source_url
    query_url = extract_url(request.query)
    has_url = url is not None

    classification = classify_query(
        request.query,
        has_url,
        source_text=request.source_text,
    )
    topics = []
    awaiting_topic_selection = False
    allow_whole_website = False
    if (
        query_url
        and request.selected_topic is None
        and classification["source"] == "website"
        and classification["action"] == "learn"
    ):
        prepared = prepare_website_learning(url)
        topics = prepared["topics"]
        awaiting_topic_selection = True
        allow_whole_website = True
        result = "Website indexed. Select a topic and ask your question."
    else:
        result = dispatch(
            classification["source"],
            classification["action"],
            request.query,
            url,
            source_text=request.source_text,
            conversation_history=request.conversation_history[-10:],
            selected_topic=request.selected_topic,
        )

    return {
        "query": request.query,
        "url": url,
        "has_url": has_url,
        "source": classification["source"],
        "action": classification["action"],
        "request_type": classification["request_type"],
        "topics": topics,
        "awaiting_topic_selection": awaiting_topic_selection,
        "allow_whole_website": allow_whole_website,
        "result": result,
    }
