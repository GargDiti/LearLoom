from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().with_name(".env"))
from services.url_detector import extract_url
from services.query_router import classify_query
from services.handlers import dispatch

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/analyze-query")
def analyze_query(request: QueryRequest):
    url = extract_url(request.query)
    has_url = url is not None

    classification = classify_query(request.query, has_url)
    result = dispatch(classification["source"], classification["action"], request.query, url)

    return {
        "query": request.query,
        "url": url,
        "has_url": has_url,
        "source": classification["source"],
        "action": classification["action"],
        "result": result,
    }
