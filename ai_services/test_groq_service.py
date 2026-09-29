from services.firecrawl_service import scrape_page
from services.topic_extractor import (
    extract_topics,
    extract_section
)
from services.groq_service import explain_topic


url = "https://nodejs.org/learn/manipulating-files/nodejs-file-paths"


# STEP 1: Scrape the website
result = scrape_page(url)

print("Website scraped successfully.")


# STEP 2: Get markdown from Firecrawl response
markdown = result["markdown"]

print("Markdown received.")


# STEP 3: Extract topics
topics = extract_topics(markdown)

print("\nTopics found:")

for i, topic in enumerate(topics):
    print(i, topic["title"])


# STEP 4: Simulate the user selecting a topic
selected_topic = topics[1]["title"]

print("\nSelected topic:", selected_topic)


# STEP 5: Extract only the selected topic's content
content = extract_section(
    markdown,
    selected_topic
)

print("\nSelected content:")
print(content[:1000])


# STEP 6: Send selected content to Groq
answer = explain_topic(
    selected_topic,
    content
)

print("\nAI Tutor Response:")
print(answer)