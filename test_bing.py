import feedparser
from brain.sentiment.scraper import fetch_url
import time

ticker = "TSLA"
rss_url = f"https://www.bing.com/news/search?q={ticker}+stock&format=rss"

print(f"Fetching RSS: {rss_url}")
feed = feedparser.parse(rss_url)

if not feed.entries:
    print("No entries found.")
else:
    print(f"Found {len(feed.entries)} entries.")
    for i in range(min(3, len(feed.entries))):
        entry = feed.entries[i]
        print(f"\nTitle: {entry.title}")
        print(f"Link: {entry.link}")
        
        # Try scraping
        print("Scraping...")
        text, status, t = fetch_url(entry.link, timeout=4.0)
        print(f"Status: {status}")
        print(f"Text Length: {len(text) if text else 0}")
        print(f"Snippet: {text[:100] if text else 'None'}")
