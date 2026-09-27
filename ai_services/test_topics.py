from services.firecrawl_service import scrape_page
from services.topic_extractor import extract_section, extract_topics


url = "https://nodejs.org/learn/manipulating-files/nodejs-file-paths"

# 1. Get the response from Firecrawl
result = scrape_page(url)

# 2. Take the markdown from the Firecrawl response
markdown = result["markdown"]

# 3. Give that markdown to the topic extractor
topics = extract_topics(markdown)

# 4. Display the topics
print("\nTopics found:\n")

for topic in topics:
    print(topic)

selected_topic = topics[1]["title"]

print("\nSelected topic:")
print(selected_topic)

section = extract_section(
    markdown,
    selected_topic
)

print("\nSelected topic content:\n")
print(section)