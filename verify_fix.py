
import requests
import json
import sys

def verify():
    url = "http://localhost:5000/api/analyze?ticker=AAPL"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"FAILED: Status Code {response.status_code}")
            return

        data = response.json()
        news = data.get("news", [])
        
        print(f"Success: Status 200")
        print(f"Article Count: {len(news)}")
        
        zeros = [n for n in news if n.get('sentiment_score') == 0.0]
        print(f"Zero Score Articles: {len(zeros)}")
        
        if len(news) == 20:
            print("PASS: Exactly 20 articles.")
        else:
            print(f"FAIL: Expected 20 articles, got {len(news)}")
            
        if len(zeros) == 0:
            print("PASS: No 0.0 sentiment scores.")
        else:
            print(f"FAIL: Found {len(zeros)} articles with 0.0 score.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
