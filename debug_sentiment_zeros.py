import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from brain.sentiment.news import fetch_google_news
from brain.sentiment.analyzer import analyze_sentiment

print("--- Debugging 0.00 Sentiment Scores ---")
ticker = "MSFT" 
news, _ = fetch_google_news(ticker)

zeros = [n for n in news if abs(n['sentiment']) < 0.01]

print(f"Found {len(zeros)} zero-score items out of {len(news)} total.")

if zeros:
    # Check the first one
    n = zeros[0]
    print(f"\nExample Title: {n['title']}")
    
    # Re-fetch raw feed entry to see description (since news.py doesn't return it in the dict)
    import feedparser
    rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:3d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    # Find the matching entry
    matching_entry = next((e for e in feed.entries if e.title == n['title']), None)
    
    if matching_entry:
        desc = matching_entry.description if hasattr(matching_entry, 'description') else "NO DESC"
        print(f"Raw Description: {desc}")
        
        combined = f"{n['title']}. {desc}"
        print(f"Combined Length: {len(combined)}")
        
        print("\nRe-Running Main Analyzer on Combined Text:")
        score = analyze_sentiment(combined)
        print(f"Score: {score}")
        
    else:
        print("Could not find matching RSS entry to inspect description.")
