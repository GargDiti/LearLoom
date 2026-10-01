from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().with_name(".env"))
from services.handlers import dispatch
from services.query_router import Action, Source, classify_query
from services.url_detector import extract_url

def main():
    query = input("Enter a learning query: ").strip()
    if not query:
        print("Please enter a query.")
        return

    url = extract_url(query)

    try:
        classification = classify_query(query, has_url=url is not None)
    except Exception as error:
        print(f"Could not classify the query: {type(error).__name__}: {error}")
        return

    source = classification["source"]
    action = classification["action"]
    print(f"\nQuery type: {source.value}")
    print(f"Requested action: {action.value}")

    if source != Source.GENERAL:
        print("This test handles general queries. Try a query without a webpage URL.")
        return

    if action != Action.LEARN:
        print("General quiz handling is not implemented yet; try asking to learn or explain a topic.")
        return

    try:
        answer = dispatch(source, action, query, url)
    except Exception as error:
        print(f"Could not generate an explanation: {type(error).__name__}: {error}")
        return

    if answer and answer.strip():
        print("\nLearnLoom Explanation:\n")
        print(answer)
    else:
        print("The AI returned an empty response.")


if __name__ == "__main__":
    main()