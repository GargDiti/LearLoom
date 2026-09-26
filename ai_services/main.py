from fastapi import FastAPI
from pydantic import BaseModel
from services.url_detector import extract_url
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/analyze-query")
def analyze_query(request: QueryRequest):

    url = extract_url(request.query)

    return {
        "query": request.query,
        "url": url,
        "has_url": url is not None
    }