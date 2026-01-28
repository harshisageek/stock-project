
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from brain.sentiment.news import fetch_gnews

print("--- START DEBUG ---")
ticker = "AAPL"
print(f"Calling fetch_gnews('{ticker}')...")

try:
    articles, score = fetch_gnews(ticker)
    print(f"Finished fetch_gnews.")
    print(f"Count: {len(articles)}")
    print(f"Score: {score}")
    
    if len(articles) == 0:
        print("ZERO ARTICLES returned. Checking why...")
        # Since I added debug prints in news.py, they should appear above.
        
except Exception as e:
    print(f"EXCEPTION: {e}")

print("--- END DEBUG ---")
