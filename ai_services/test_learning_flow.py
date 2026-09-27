from services.url_detector import extract_url
from services.firecrawl_service import scrape_page
from services.groq_services import explain_topic
from services.topic_extractor import extract_section, extract_topics


def main() -> None:

    # Simulate the actual query entered by the user.
    user_query = input("\nEnter your learning query:\n> ")

    # ---------------------------------------------------------
    # STEP 1: Extract URL from the user's query
    # ---------------------------------------------------------

    url = extract_url(user_query)

    if not url:
        print("\nNo URL was found in your query.")
        print("Please provide a URL if you want to learn from a website.")
        return

    print(f"\nURL detected: {url}")

    # ---------------------------------------------------------
    # STEP 2: Send the extracted URL to Firecrawl
    # ---------------------------------------------------------

    print("\nScraping website...")

    try:
        result = scrape_page(url)
    except Exception as error:
        print(
            f"Firecrawl request failed "
            f"({type(error).__name__}): {error}"
        )
        return

    # ---------------------------------------------------------
    # STEP 3: Get Markdown from Firecrawl response
    # ---------------------------------------------------------

    markdown = result.get("markdown", "")

    if not markdown.strip():
        print("\nFirecrawl returned empty markdown.")
        return

    print("Website content received successfully.")

    # ---------------------------------------------------------
    # STEP 4: Extract topics from the Markdown
    # ---------------------------------------------------------

    topics = extract_topics(markdown)

    if not topics:
        print("\nNo topics were found on this webpage.")
        return

    print("\nTopics found:\n")

    for index, topic in enumerate(topics, start=1):
        print(
            f"{index}. "
            f"H{topic['level']}: "
            f"{topic['title']}"
        )

    # ---------------------------------------------------------
    # STEP 5: Let the user select a topic
    # ---------------------------------------------------------

    while True:

        try:
            choice = int(
                input(
                    "\nEnter the number of the topic "
                    "you want to learn:\n> "
                )
            )

            if 1 <= choice <= len(topics):
                break

            print(
                f"Please enter a number between "
                f"1 and {len(topics)}."
            )

        except ValueError:
            print("Please enter a valid number.")

    selected_topic = topics[choice - 1]["title"]

    print(f"\nSelected topic: {selected_topic}")

    # ---------------------------------------------------------
    # STEP 6: Extract only the selected topic's section
    # ---------------------------------------------------------

    content = extract_section(
        markdown,
        selected_topic
    )

    if not content.strip():
        print(
            f"\nNo content was found for "
            f"'{selected_topic}'."
        )
        return

    print("\nSelected content preview:")
    print("-" * 60)
    print(content[:1000])
    print("-" * 60)

    # ---------------------------------------------------------
    # STEP 7: Send selected content to Groq
    # ---------------------------------------------------------

    print("\nGenerating explanation using Groq...")

    try:
        explanation = explain_topic(
            selected_topic,
            content
        )

    except Exception as error:
        print(
            f"Groq request failed "
            f"({type(error).__name__}): {error}"
        )
        return

    if not explanation or not explanation.strip():
        print("\nGroq returned an empty explanation.")
        return

    # ---------------------------------------------------------
    # STEP 8: Display the AI explanation
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("AI TUTOR EXPLANATION")
    print("=" * 60)

    print(explanation)


if __name__ == "__main__":
    main()
