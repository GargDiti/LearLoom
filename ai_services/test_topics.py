from services.firecrawl_service import scrape_page
from services.topic_extractor import extract_topics


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