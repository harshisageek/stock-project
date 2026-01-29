import os
from backend.database import NewsDatabase
from dotenv import load_dotenv

load_dotenv()

db = NewsDatabase()
ticker = "AAPL"

print(f"Fetching latest news for {ticker} from DB...")
articles = db.get_latest_news(ticker, limit=20)

print(f"Found {len(articles)} articles.")
for i, art in enumerate(articles):
    score = art.get('sentiment_score')
    title = art.get('title', 'No Title')[:30]
    print(f"[{i}] Score: {score} (Type: {type(score)}) - {title}...")

print("\nRunning Check against filter abs(x) < 0.05:")
for i, art in enumerate(articles):
    score = art.get('sentiment_score')
    try:
        if abs(score) < 0.05:
            print(f"FAIL: Article {i} has weak score {score}")
        else:
            print(f"PASS: Article {i} has score {score}")
    except Exception as e:
        print(f"ERROR: Article {i} caused {e}")
