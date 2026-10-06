
from services.vector_store import search_chunks
from services.groq_service import answer_from_context


def main():
    source_url = "https://example.com/learnloom-test"

    question = "How does Node.js handle asynchronous operations?"

    chunks = search_chunks(
        query=question,
        source_url=source_url,
        top_k=3
    )

    print("Retrieved chunks:", len(chunks))

    answer = answer_from_context(
        query=question,
        retrieved_chunks=chunks
    )

    print("\nLearnLoom's answer:\n")
    print(answer)


if __name__ == "__main__":
    main()
