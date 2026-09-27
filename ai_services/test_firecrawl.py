from services.firecrawl_service import scrape_page

print("1. Test file started")

url = "https://nodejs.org/learn/manipulating-files/nodejs-file-paths"

print("2. Calling Firecrawl...")

result = scrape_page(url)

print("3. Firecrawl returned a response")

print("URL:", result["url"])
print("TITLE:", result["title"])

print("\nMARKDOWN:")
print(result["markdown"][:2000])

print("\n4. Test completed")