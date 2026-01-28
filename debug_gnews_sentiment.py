import sys
import os
from dotenv import load_dotenv

# Ensure backend modules can be imported
sys.path.append(os.getcwd())
load_dotenv()

from brain.sentiment.news import fetch_gnews
from brain.sentiment.analyzer import analyze_sentiment
from brain.sentiment.analyzer import analyze_sentiment

print("--- Debugging GNews Sentiment (Why so many 0.00?) ---")
ticker = "NVDA" 
print(f"Fetching news for {ticker}...")

news, avg = fetch_gnews(ticker)

zeros = [n for n in news if abs(n['sentiment']) < 0.001]
others = [n for n in news if abs(n['sentiment']) >= 0.001]

print(f"\nTotal: {len(news)}")
print(f"Zero/Neutral: {len(zeros)} ({len(zeros)/len(news)*100:.1f}%)")
print(f"Non-Zero: {len(others)}")

if zeros:
    print("\n--- Deep Dive into First 3 Zero-Score Articles ---")
    for i, n in enumerate(zeros[:3]):
        print(f"\n[{i+1}] Title: {n['title']}")
        print(f"    Link: {n['link']}")
        
        # We need to reconstruct the full text logic from news.py to see what happened
        # Logic in news.py: full_text = f"{title}. {desc} {content}"
        # We don't have raw desc/content here, but we can verify if the *Title* itself has sentiment.
        
        print("    Running Analyzer on Title Only:")
        title_score = analyze_sentiment(n['title'])
        print(f"    Title Score: {title_score}")
        
        # If title has score but final is 0, getting diluted or content is weird?
        if abs(title_score) > 0.1:
            print("    [SUSPICIOUS] Title is emotional, but final score is 0.00.")
        else:
            print("    [EXPECTED] Title is also neutral.")
            
else:
    print("No zero scores found in this run!")
