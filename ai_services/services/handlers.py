import hashlib

from services.firecrawl_service import scrape_page
from services.groq_service import answer_from_context, explain_general_query
from services.query_router import Action, Source
from services.text_chunker import chunk_markdown
from services.topic_extractor import extract_topics
from services.vector_store import index_chunks, search_chunks


def handle_general_learn(
    query: str,
    conversation_history: list[dict] | None = None,
) -> str:
    if conversation_history is None:
        return explain_general_query(query)
    return explain_general_query(query, conversation_history)

def _answer_from_source(
    query: str,
    source_text: str,
    source_key: str,
    retrieval_query: str | None = None,
    conversation_history: list[dict] | None = None,
) -> str:
    chunks = chunk_markdown(source_text)
    if not chunks:
        raise ValueError("No text chunks could be created from the learning source.")

    index_chunks(source_key, chunks)
    retrieval_query = retrieval_query or query.strip() or chunks[0]["text"][:500]
    retrieved_chunks = search_chunks(retrieval_query, source_key, top_k=4)
    answer_query = query.strip() or "Summarize and explain the key ideas in this source."
    if conversation_history is None:
        return answer_from_context(answer_query, retrieved_chunks)
    return answer_from_context(
        answer_query,
        retrieved_chunks,
        conversation_history,
    )


def handle_website_learn(
    query: str,
    url: str,
    conversation_history: list[dict] | None = None,
) -> str:
    result = scrape_page(url)
    markdown = result.get("markdown", "") if isinstance(result, dict) else ""
    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError("Firecrawl returned no Markdown content.")

    topics = extract_topics(markdown)
    topic_context = "\n".join(topic["title"] for topic in topics)
    question = query.replace(url, " ").strip()
    if not question:
        question = "Teach me the key ideas from this website."
    retrieval_query = "\n".join(part for part in (question, topic_context) if part)
    return _answer_from_source(
        question,
        markdown,
        url,
        retrieval_query,
        conversation_history,
    )


def handle_source_text_learn(
    query: str,
    source_text: str | None = None,
    conversation_history: list[dict] | None = None,
) -> str:
    source = source_text if source_text and source_text.strip() else query
    question = query if source_text and source_text.strip() else ""
    source_key = "source-text:" + hashlib.sha256(source.encode("utf-8")).hexdigest()
    retrieval_query = "\n".join((question, source[:500])).strip()
    return _answer_from_source(
        question,
        source,
        source_key,
        retrieval_query,
        conversation_history,
    )

def handle_general_quiz(query: str):
    # TODO: Groq generates a quiz directly from the named topic
    pass

def handle_website_quiz(query: str, url: str):
    # TODO: Firecrawl scrapes relevant content -> Groq generates quiz from that content only
    pass

def dispatch(
    source: Source,
    action: Action,
    query: str,
    url: str | None,
    source_text: str | None = None,
    conversation_history: list[dict] | None = None,
):
    if source == Source.GENERAL and action == Action.LEARN:
        return handle_general_learn(query, conversation_history)
    if source == Source.WEBSITE and action == Action.LEARN:
        if not url:
            raise ValueError("A URL is required for website learning.")
        return handle_website_learn(query, url, conversation_history)
    if source == Source.SOURCE_TEXT and action == Action.LEARN:
        return handle_source_text_learn(query, source_text, conversation_history)
    if source == Source.GENERAL and action == Action.QUIZ:
        return handle_general_quiz(query)
    if source == Source.WEBSITE and action == Action.QUIZ:
        return handle_website_quiz(query, url)