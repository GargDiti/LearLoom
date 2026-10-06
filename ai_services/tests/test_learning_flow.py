import io
import re
import unittest
from contextlib import redirect_stdout
from urllib.parse import urlsplit
from unittest.mock import patch

from services.firecrawl_service import scrape_page
from services.groq_service import answer_from_context, explain_general_query
from services.handlers import dispatch
from services.query_router import Action, RequestType, Source, classify_query
from services.text_chunker import chunk_markdown
from services.topic_extractor import extract_section, extract_topics
from services.url_detector import extract_url
from services.vector_store import index_chunks, search_chunks


def run_learning_flow(user_input: str, input_fn=input) -> bool:
    user_input = user_input.strip()
    if not user_input:
        print("Please enter a topic or question to learn about.")
        return False

    url = extract_url(user_input)

    if not url:
        if re.search(r"https?://", user_input, re.IGNORECASE):
            print("The URL looks incomplete. Please provide a valid website URL.")
            return False

        print("\nNo website URL found. Answering your general learning query...")
        try:
            answer = explain_general_query(user_input)
        except Exception as error:
            print(f"Groq generation failed: {error}")
            return False

        if not isinstance(answer, str) or not answer.strip():
            print("Groq returned an empty answer.")
            return False

        print("\n" + "=" * 60)
        print("LEARNLOOM GENERAL ANSWER")
        print("=" * 60)
        print(answer)
        print("=" * 60)
        return True

    try:
        parsed_url = urlsplit(url)
        valid_url = (
            parsed_url.scheme in {"http", "https"}
            and bool(parsed_url.hostname)
        )
    except ValueError:
        valid_url = False

    if not valid_url:
        print("No valid HTTP or HTTPS URL found. Please include a website URL.")
        return False

    print("\n[1/5] Scraping website...")

    try:
        result = scrape_page(url)
    except Exception as error:
        print(f"Scraping failed: {error}")
        return False

    markdown = result.get("markdown", "") if isinstance(result, dict) else ""
    if not isinstance(markdown, str) or not markdown.strip():
        print("Firecrawl returned empty Markdown.")
        return False

    print(f"Scraped {len(markdown)} characters.")
    topics = extract_topics(markdown)
    selectable_topics = []

    print("\nTopics found:")
    for topic in topics:
        title = topic["title"]
        content = extract_section(markdown, title)
        if not content.strip():
            continue

        selectable_topics.append(title)
        print(f"{len(selectable_topics)}. H{topic['level']}: {title}")

    if not selectable_topics:
        print("No topic sections with content were found.")

    print("\n[2/5] Creating text chunks...")
    try:
        chunks = chunk_markdown(markdown)
    except Exception as error:
        print(f"Chunking failed: {error}")
        return False

    if not chunks:
        print("No chunks were created.")
        return False

    print(f"Created {len(chunks)} chunks.")
    print("\n[3/5] Building and storing TF-IDF vectors...")

    try:
        indexed_count = index_chunks(url, chunks)
    except Exception as error:
        print(f"Indexing failed: {error}")
        return False

    print(f"Chunks indexed: {indexed_count}")
    print("\n0. Search the entire website")

    try:
        selection = int(
            input_fn("Select a topic number (or 0 for the whole site): ")
        )
    except (TypeError, ValueError):
        print("Please enter a valid topic number.")
        return False

    selected_topic = None
    if selection == 0:
        print("\nSearching the entire website.")
    elif 1 <= selection <= len(selectable_topics):
        selected_topic = selectable_topics[selection - 1]
        print(f'\nSelected topic: "{selected_topic}"')
    else:
        print("That topic number is out of range.")
        return False

    question = input_fn("\nEnter your question about the website: ").strip()
    if not question:
        print("Please enter a question.")
        return False

    retrieval_query = (
        f"{selected_topic}\n{question}"
        if selected_topic
        else question
    )

    print("\n[4/5] Searching for relevant content...")
    try:
        retrieved_chunks = search_chunks(
            query=retrieval_query,
            source_url=url,
            top_k=4,
        )
    except Exception as error:
        print(f"Retrieval failed: {error}")
        return False

    if not retrieved_chunks:
        print(
            "No relevant chunks were found on this website. "
            "Try rephrasing your question."
        )
        return False

    if any(chunk.get("source_url") != url for chunk in retrieved_chunks):
        print("Retrieval returned content from a different website; stopping.")
        return False

    print(f"\nRetrieved {len(retrieved_chunks)} chunks:")
    for rank, chunk in enumerate(retrieved_chunks, start=1):
        print(f"\nResult {rank}")
        print(f"Section: {chunk['section_title']}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Similarity: {chunk['similarity']:.4f}")
        print(f"Preview: {' '.join(chunk['text'].split())[:250]}")

    print("\n[5/5] Asking Groq to answer from retrieved context...")
    try:
        answer = answer_from_context(
            query=question,
            retrieved_chunks=retrieved_chunks,
        )
    except Exception as error:
        print(f"Groq generation failed: {error}")
        return False

    if not isinstance(answer, str) or not answer.strip():
        print("Groq returned an empty answer.")
        return False

    print("\n" + "=" * 60)
    print("LEARNLOOM RAG ANSWER")
    print("=" * 60)
    print(answer)
    print("=" * 60)
    print(f"\nPipeline completed for {url}.")
    print(f"Chunks indexed: {indexed_count}")
    print(f"Chunks retrieved: {len(retrieved_chunks)}")
    return True


class LearningFlowTests(unittest.TestCase):
    def setUp(self):
        self.url = "https://docs.example.org/guide"
        self.markdown = (
            "# [Getting Started](https://docs.example.org/start)\n\n"
            "This guide introduces the runtime and its core features.\n\n"
            "## **Installation**\n\n"
            "Install the runtime and verify the local setup."
        )

    def _inputs(self, selection="1", question="How do I install it?"):
        values = iter((selection, question))
        return lambda _prompt: next(values)

    def _report_path(self, request_type, called, skipped, result):
        print(f"REQUEST TYPE: {request_type.value}")
        print(f"SERVICES CALLED: {', '.join(called)}")
        print(f"SERVICES SKIPPED: {', '.join(skipped)}")
        print(f"FINAL RESULT: {'PASS' if result else 'FAIL'}")

    def test_router_sends_short_general_query_directly_to_groq(self):
        query = "Explain polymorphism in Java"
        url = extract_url(query)
        classification = classify_query(query, has_url=url is not None)

        with (
            patch("services.handlers.explain_general_query", return_value="Polymorphism lets types share an interface.") as explain,
            patch("services.handlers.scrape_page") as scrape,
            patch("services.handlers.chunk_markdown") as chunk,
            patch("services.handlers.index_chunks") as index,
            patch("services.handlers.search_chunks") as search,
        ):
            answer = dispatch(
                classification["source"],
                classification["action"],
                query,
                url,
            )

        self.assertIsNone(url)
        self.assertEqual(classification["request_type"], RequestType.GENERAL_LEARNING)
        self.assertEqual(answer, "Polymorphism lets types share an interface.")
        explain.assert_called_once_with(query)
        scrape.assert_not_called()
        chunk.assert_not_called()
        index.assert_not_called()
        search.assert_not_called()
        self._report_path(
            RequestType.GENERAL_LEARNING,
            ["URL detector", "router", "Groq"],
            ["Firecrawl", "topic extraction", "chunking", "vector indexing", "retrieval"],
            bool(answer),
        )

    def test_router_runs_website_rag_pipeline(self):
        query = f"Explain Node.js from {self.url}"
        url = extract_url(query)
        classification = classify_query(query, has_url=url is not None)
        retrieved = [{"text": "Node.js runs JavaScript outside a browser."}]

        with (
            patch("services.handlers.scrape_page", return_value={"markdown": self.markdown}) as scrape,
            patch("services.handlers.extract_topics", return_value=[{"title": "Getting Started"}]) as topics,
            patch("services.handlers.chunk_markdown", return_value=[{"chunk_id": 0, "section_title": "Intro", "text": "Node.js runtime"}]) as chunk,
            patch("services.handlers.index_chunks", return_value=1) as index,
            patch("services.handlers.search_chunks", return_value=retrieved) as search,
            patch("services.handlers.answer_from_context", return_value="Node.js runs JavaScript outside a browser.") as answer_from_context_mock,
            patch("services.handlers.explain_general_query") as explain,
        ):
            answer = dispatch(
                classification["source"],
                classification["action"],
                query,
                url,
            )

        self.assertEqual(classification["request_type"], RequestType.WEBSITE_LEARNING)
        scrape.assert_called_once_with(self.url)
        topics.assert_called_once_with(self.markdown)
        chunk.assert_called_once_with(self.markdown)
        index.assert_called_once_with(self.url, chunk.return_value)
        search.assert_called_once()
        answer_from_context_mock.assert_called_once_with(
            "Explain Node.js from", retrieved
        )
        explain.assert_not_called()
        self.assertTrue(answer)
        self._report_path(
            RequestType.WEBSITE_LEARNING,
            ["URL detector", "router", "Firecrawl", "topic extraction", "chunking", "vector indexing", "retrieval", "Groq"],
            ["general-query Groq path"],
            bool(answer),
        )

    def test_router_indexes_large_source_text_without_firecrawl(self):
        source_text = ("Polymorphism allows related objects to share behavior. " * 30)
        query = "Explain the main idea"
        classification = classify_query(
            query,
            has_url=False,
            source_text=source_text,
        )
        retrieved = [{"text": source_text[:100]}]

        with (
            patch("services.handlers.scrape_page") as scrape,
            patch("services.handlers.chunk_markdown", return_value=[{"chunk_id": 0, "text": source_text}]) as chunk,
            patch("services.handlers.index_chunks", return_value=1) as index,
            patch("services.handlers.search_chunks", return_value=retrieved) as search,
            patch("services.handlers.answer_from_context", return_value="Polymorphism is shared behavior across types.") as answer_from_context_mock,
            patch("services.handlers.explain_general_query") as explain,
        ):
            answer = dispatch(
                classification["source"],
                classification["action"],
                query,
                None,
                source_text=source_text,
            )

        self.assertEqual(classification["request_type"], RequestType.SOURCE_TEXT_LEARNING)
        self.assertEqual(classification["source"], Source.SOURCE_TEXT)
        self.assertEqual(classification["action"], Action.LEARN)
        scrape.assert_not_called()
        chunk.assert_called_once_with(source_text)
        index.assert_called_once()
        self.assertTrue(index.call_args.args[0].startswith("source-text:"))
        search.assert_called_once()
        answer_from_context_mock.assert_called_once_with(query, retrieved)
        explain.assert_not_called()
        self.assertTrue(answer)
        self._report_path(
            RequestType.SOURCE_TEXT_LEARNING,
            ["router", "chunking", "vector indexing", "retrieval", "Groq"],
            ["Firecrawl", "topic extraction", "general-query Groq path"],
            bool(answer),
        )

    def test_general_query_without_url_calls_groq(self):
        query = "Help me understand how the Node.js event loop works"
        output = io.StringIO()
        with (
            patch("test_learning_flow.explain_general_query", return_value="The event loop schedules asynchronous work.") as explain,
            patch("test_learning_flow.scrape_page") as scrape,
            redirect_stdout(output),
        ):
            succeeded = run_learning_flow(f"  {query}  ")

        self.assertTrue(succeeded)
        explain.assert_called_once_with(query)
        scrape.assert_not_called()
        self.assertIn("LEARNLOOM GENERAL ANSWER", output.getvalue())
        self.assertIn("The event loop schedules asynchronous work.", output.getvalue())

    def test_general_query_groq_error_is_reported(self):
        with (
            patch("test_learning_flow.explain_general_query", side_effect=RuntimeError("Groq unavailable")) as explain,
            patch("test_learning_flow.scrape_page") as scrape,
        ):
            self.assertFalse(run_learning_flow("Explain recursion"))

        explain.assert_called_once_with("Explain recursion")
        scrape.assert_not_called()

    def test_scrape_index_retrieve_then_answer(self):
        retrieved = [{
            "source_url": self.url,
            "section_title": "Installation",
            "chunk_id": 1,
            "similarity": 0.82,
            "text": "Install the runtime and verify the local setup.",
        }]
        events = []

        def retrieve(**kwargs):
            events.append("retrieve")
            self.assertEqual(kwargs["source_url"], self.url)
            self.assertIn("Getting Started", kwargs["query"])
            self.assertIn("How do I install it?", kwargs["query"])
            return retrieved

        def answer(**kwargs):
            events.append("answer")
            self.assertEqual(kwargs["query"], "How do I install it?")
            self.assertIs(kwargs["retrieved_chunks"], retrieved)
            return "Use the installation instructions from the page."

        output = io.StringIO()
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}) as scrape,
            patch("test_learning_flow.index_chunks", return_value=2) as index,
            patch("test_learning_flow.search_chunks", side_effect=retrieve),
            patch("test_learning_flow.answer_from_context", side_effect=answer),
            redirect_stdout(output),
        ):
            succeeded = run_learning_flow(
                f"Help me learn from {self.url}",
                self._inputs(),
            )

        self.assertTrue(succeeded)
        scrape.assert_called_once_with(self.url)
        indexed_chunks = index.call_args.args[1]
        self.assertGreater(len(indexed_chunks), 0)
        self.assertEqual(events, ["retrieve", "answer"])
        self.assertIn("Chunks indexed: 2", output.getvalue())
        self.assertIn("Getting Started", output.getvalue())
        self.assertNotIn("[Getting Started]", output.getvalue())
        self.assertIn("Section: Installation", output.getvalue())
        self.assertIn("Chunk ID: 1", output.getvalue())
        self.assertIn("Similarity: 0.8200", output.getvalue())
        self.assertIn("Preview: Install the runtime", output.getvalue())

    def test_whole_website_search_uses_only_the_question(self):
        retrieved = [{
            "source_url": self.url,
            "section_title": "Installation",
            "chunk_id": 1,
            "similarity": 0.82,
            "text": "Install the runtime.",
        }]

        def retrieve(**kwargs):
            self.assertEqual(kwargs["query"], "How do I install it?")
            self.assertEqual(kwargs["source_url"], self.url)
            return retrieved

        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks", side_effect=retrieve),
            patch("test_learning_flow.answer_from_context", return_value="Answer"),
        ):
            self.assertTrue(
                run_learning_flow(
                    self.url,
                    self._inputs(selection="0"),
                )
            )

    def test_no_relevant_chunks_do_not_call_groq(self):
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks", return_value=[]),
            patch("test_learning_flow.answer_from_context") as answer,
        ):
            self.assertFalse(
                run_learning_flow(self.url, self._inputs())
            )
        answer.assert_not_called()

    def test_invalid_url_does_not_scrape(self):
        with patch("test_learning_flow.scrape_page") as scrape:
            self.assertFalse(run_learning_flow("learn from https://"))
        scrape.assert_not_called()

    def test_empty_scrape_stops_before_indexing(self):
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": "  "}),
            patch("test_learning_flow.index_chunks") as index,
        ):
            self.assertFalse(run_learning_flow(self.url))
        index.assert_not_called()

    def test_invalid_topic_selection_stops_before_retrieval(self):
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks") as search,
        ):
            self.assertFalse(
                run_learning_flow(
                    self.url,
                    self._inputs(selection="9"),
                )
            )
        search.assert_not_called()

    def test_retrieval_error_does_not_call_groq(self):
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks", side_effect=RuntimeError("index unavailable")),
            patch("test_learning_flow.answer_from_context") as answer,
        ):
            self.assertFalse(
                run_learning_flow(self.url, self._inputs())
            )
        answer.assert_not_called()

    def test_wrong_website_results_do_not_call_groq(self):
        wrong_site = [{
            "source_url": "https://other.example.org/",
            "section_title": "Other",
            "chunk_id": 0,
            "similarity": 0.9,
            "text": "Unrelated content.",
        }]
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks", return_value=wrong_site),
            patch("test_learning_flow.answer_from_context") as answer,
        ):
            self.assertFalse(
                run_learning_flow(self.url, self._inputs())
            )
        answer.assert_not_called()

    def test_groq_error_is_reported(self):
        retrieved = [{
            "source_url": self.url,
            "section_title": "Installation",
            "chunk_id": 1,
            "similarity": 0.82,
            "text": "Install the runtime.",
        }]
        with (
            patch("test_learning_flow.scrape_page", return_value={"markdown": self.markdown}),
            patch("test_learning_flow.index_chunks", return_value=2),
            patch("test_learning_flow.search_chunks", return_value=retrieved),
            patch("test_learning_flow.answer_from_context", side_effect=RuntimeError("Groq unavailable")),
        ):
            self.assertFalse(
                run_learning_flow(self.url, self._inputs())
            )


def main():
    user_input = input("Enter a learning query containing a website URL: ").strip()
    run_learning_flow(user_input)


if __name__ == "__main__":
    main()