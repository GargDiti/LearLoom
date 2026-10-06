import unittest
from types import SimpleNamespace
from unittest.mock import patch

from main import QueryRequest, analyze_query
from services.groq_service import answer_from_context, explain_general_query
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
        )


if __name__ == "__main__":
    unittest.main()
