
import logging
import os
from dotenv import load_dotenv
from brain.analysis.sentiment import SentimentEngine
import requests

load_dotenv()
logger = logging.getLogger(__name__)

# Mock fetch_gnews logic to test interaction with New Sentiment Engine
def test_fetch_and_score():
    ticker = "AAPL"
    api_key = os.getenv("GNEWS_API_KEY1")
    if not api_key:
        print("No API Key")
        return

    url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&sortby=publishedAt&max=10&token={api_key}"
    print(f"Fetching news for {ticker}...")
    
    try:
        resp = requests.get(url)
        data = resp.json()
        articles = data.get("articles", [])
        print(f"Fetched {len(articles)} articles.")
        
        titles = [a['title'] for a in articles]
        
        print("\n--- SCORING WITH NEW ENGINE ---")
        scores = SentimentEngine.analyze_batch(titles)
        
        for t, s in zip(titles, scores):
            print(f"Score: {s:.4f} | Title: {t[:50]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_and_score()

