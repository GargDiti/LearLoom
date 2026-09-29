from services.firecrawl_service import scrape_page
from services.topic_extractor import extract_section, extract_topics
from services.url_detector import extract_url


def main():
	query = input("Enter a learning query containing a URL: ").strip()

	# Detect the URL in the user's prompt and pass it to Firecrawl.
	url = extract_url(query)
	if not url:
		print("No URL found in your query. Include a page URL and try again.")
		return

	try:
		result = scrape_page(url)
	except Exception as error:
		print(f"Could not scrape the page: {error}")
		return

	# Pass Firecrawl's markdown into topic extraction, then reuse that same
	# markdown to retrieve the content for each topic shown to the user.
	markdown = result.get("markdown", "")
	if not markdown.strip():
		print("Firecrawl returned empty markdown.")
		return

	topics = extract_topics(markdown)
	if not topics:
		print("No topics were found in the page markdown.")
		return

	selectable_topics = []
	print("\nTopics found:")
	for topic in topics:
		title = topic["title"]
		content = extract_section(markdown, title)
		if not content or not content.strip():
			continue

		selectable_topics.append((title, content))
		preview = " ".join(content.split())[:240]
		print(f"{len(selectable_topics)}. H{topic['level']}: {title}")
		print(f"   Preview: {preview}")

	if not selectable_topics:
		print("No topic sections with content were found.")
		return

	try:
		selection = int(input("\nSelect a topic number: ")) - 1
	except ValueError:
		print("Enter a valid topic number.")
		return

	if selection < 0 or selection >= len(selectable_topics):
		print("That topic number is out of range.")
		return

	selected_topic, content = selectable_topics[selection]
	print(f'\nSelected topic: "{selected_topic}"')

	# Send the selected topic and its extracted section to Groq for explanation.
	try:
		from services.groq_service import explain_topic

		explanation = explain_topic(selected_topic, content)
	except Exception as error:
		print(f"Groq could not explain the selected topic: {error}")
		return

	if not explanation or not explanation.strip():
		print("Groq returned an empty explanation.")
		return

	print("\nGroq explanation:")
	print(explanation)


if __name__ == "__main__":
	main()