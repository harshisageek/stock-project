import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from brain.sentiment.news import fetch_gnews

print("--- Testing GNews Dual-Key Rotation ---")
ticker = "AAPL"
print(f"Fetching news for {ticker}...")

news, sentiment = fetch_gnews(ticker)

print(f"Items Returned: {len(news)}")
print(f"Aggregate Sentiment: {sentiment}")

if news:
    first = news[0]
    print(f"\nSample Item Debug: {first['debug']}")
    print(f"Source: {first['publisher']}")
    print(f"Title: {first['title']}")
    
    # Check if key used is logged
    if "key_used" in first['debug']:
        print(f"PASS: Key Tracking Active ({first['debug']['key_used']})")
    else:
        print("FAIL: Key usage not tracked.")
else:
    print("FAIL: No news found. Check keys or quota.")
