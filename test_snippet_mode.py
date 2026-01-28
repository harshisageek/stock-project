import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from brain.sentiment.news import fetch_google_news

print("--- Testing Snippet-Only Mode ---")
ticker = "AAPL"
print(f"Fetching news for {ticker} (Limit should be 50)...")

# Force live fetch limit logic by calling function directly
news, sentiment = fetch_google_news(ticker)

print(f"Items Returned: {len(news)}")
print(f"Aggregate Sentiment: {sentiment}")

if len(news) > 10:
    print("PASS: Limit > 10 verified.")
else:
    print(f"WARNING: Limit is {len(news)}. Check news.py.")

if len(news) > 0:
    first = news[0]
    print(f"Sample Item: {first['title'][:50]}...")
    print(f"Debug Metadata: {first['debug']}")
    
    if first['debug'].get('content_source') == 'snippet':
        print("PASS: Content Source is 'snippet'")
    else:
        print(f"FAIL: Source is {first['debug'].get('content_source')}")
else:
    print("FAIL: No news found.")
