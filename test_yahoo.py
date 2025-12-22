import feedparser
from brain.sentiment.scraper import fetch_url

ticker = "AAPL"
rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"

print(f"Fetching RSS: {rss_url}")
feed = feedparser.parse(rss_url)

if not feed.entries:
    print("No entries found.")
else:
    print(f"Found {len(feed.entries)} entries.")
    first_entry = feed.entries[0]
    print(f"Title: {first_entry.title}")
    print(f"Link: {first_entry.link}")
    
    # Try scraping the first link
    print("Scraping first link...")
    text, status, time = fetch_url(first_entry.link, timeout=4.0)
    print(f"Status: {status}")
    print(f"Text Length: {len(text) if text else 0}")
    print(f"Snippet: {text[:200] if text else 'None'}")
