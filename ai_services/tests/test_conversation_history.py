import unittest
from types import SimpleNamespace
from unittest.mock import patch

from main import QueryRequest, analyze_query
from services.groq_service import answer_from_context, explain_general_query
from services.handlers import handle_website_learn
from services.query_router import Action, RequestType, Source


class ConversationHistoryTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            {"role": "user", "content": "What is Node.js?"},
            {"role": "assistant", "content": "Node.js is a JavaScript runtime."},
        ]

    @staticmethod
    def _groq_response(answer="Contextual answer"):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=answer))]
        )

    def test_general_groq_prompt_receives_conversation_history(self):
        with patch(
            "services.groq_service.client.chat.completions.create",
            return_value=self._groq_response(),
        ) as create:
            answer = explain_general_query("Why is it fast?", self.history)

        self.assertEqual(answer, "Contextual answer")
        prompt = create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("Previous conversation:", prompt)
        self.assertIn("USER: What is Node.js?", prompt)
        self.assertIn("ASSISTANT: Node.js is a JavaScript runtime.", prompt)
        self.assertIn("Why is it fast?", prompt)

    def test_rag_groq_prompt_separates_history_context_and_current_question(self):
        chunks = [{
            "section_title": "Introduction",
            "text": "Node.js uses an event-driven, non-blocking architecture.",
        }]
        with patch(
            "services.groq_service.client.chat.completions.create",
            return_value=self._groq_response(),
        ) as create:
            answer = answer_from_context("Why is it fast?", chunks, self.history)

        self.assertEqual(answer, "Contextual answer")
        prompt = create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("Conversation history:", prompt)
        self.assertIn("Retrieved website context:", prompt)
        self.assertIn("Current question:", prompt)
        self.assertIn("USER: What is Node.js?", prompt)
        self.assertIn("event-driven, non-blocking architecture", prompt)
        self.assertIn("Why is it fast?", prompt)

    def test_follow_up_source_url_and_history_are_forwarded_to_existing_dispatch(self):
        source_url = "https://nodejs.org/learn/getting-started/introduction-to-nodejs"
        request = QueryRequest(
            query="Why is it fast?",
            source_url=source_url,
            conversation_history=self.history,
        )
        classification = {
            "source": Source.WEBSITE,
            "action": Action.LEARN,
            "request_type": RequestType.WEBSITE_LEARNING,
        }
        with (
            patch("main.classify_query", return_value=classification),
            patch("main.dispatch", return_value="Contextual answer") as dispatch,
        ):
            result = analyze_query(request)

        self.assertEqual(result["url"], source_url)
        self.assertTrue(result["has_url"])
        self.assertEqual(result["result"], "Contextual answer")
        dispatch.assert_called_once_with(
            Source.WEBSITE,
            Action.LEARN,
            "Why is it fast?",
            source_url,
            source_text=None,
            conversation_history=self.history,
            selected_topic=None,
        )

    def test_initial_website_request_returns_topics_for_selection(self):
        source_url = "https://docs.example.org/guide"
        request = QueryRequest(query=f"Learn from {source_url}")
        classification = {
            "source": Source.WEBSITE,
            "action": Action.LEARN,
            "request_type": RequestType.WEBSITE_LEARNING,
        }
        topics = [{"level": 1, "title": "Getting Started"}]
        with (
            patch("main.classify_query", return_value=classification),
            patch(
                "main.prepare_website_learning",
                return_value={"topics": topics, "indexed_chunks": 2},
            ) as prepare,
            patch("main.dispatch") as dispatch,
        ):
            result = analyze_query(request)

        prepare.assert_called_once_with(source_url)
        dispatch.assert_not_called()
        self.assertEqual(result["topics"], topics)
        self.assertTrue(result["awaiting_topic_selection"])
        self.assertTrue(result["allow_whole_website"])

    def test_selected_topic_is_used_for_website_retrieval(self):
        url = "https://docs.example.org/guide"
        retrieved = [{"text": "The event loop schedules asynchronous work."}]
        with (
            patch("services.handlers.scrape_page", return_value={"markdown": "# Introduction\nDetails"}),
            patch("services.handlers.extract_topics", return_value=[{"level": 1, "title": "Introduction"}]),
            patch("services.handlers.extract_section", return_value="Details"),
            patch("services.handlers.chunk_markdown", return_value=[{"chunk_id": 0, "text": "Details"}]),
            patch("services.handlers.index_chunks", return_value=1),
            patch("services.handlers.search_chunks", return_value=retrieved) as search,
            patch("services.handlers.answer_from_context", return_value="Answer") as answer,
        ):
            result = handle_website_learn(
                "Why is it fast?",
                url,
                self.history,
                "Introduction",
            )

        self.assertEqual(result, "Answer")
        search.assert_called_once_with(
            "Why is it fast?\nIntroduction",
            url,
            top_k=4,
        )
        answer.assert_called_once_with("Why is it fast?", retrieved, self.history)


if __name__ == "__main__":
    unittest.main()
