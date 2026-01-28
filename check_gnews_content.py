
import os
import sys
from dotenv import load_dotenv
import requests

# Load env vars
load_dotenv()

api_key = os.getenv("GNEWS_API_KEY1") or os.getenv("GNEWS_API_KEY2")
if not api_key:
    print("No API Key found")
    sys.exit(1)

ticker = "AAPL"
url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&sortby=publishedAt&token={api_key}"

print(f"Fetching from: {url.replace(api_key, 'HIDDEN')}")

try:
    resp = requests.get(url)
    data = resp.json()
    
    if "articles" not in data:
        print("No articles found or error:", data)
    else:
        articles = data['articles']
        print(f"Found {len(articles)} articles.")
        if articles:
            first = articles[0]
            print("\n--- First Article ---")
            print(f"Title: {first.get('title')}")
            print(f"Description: {first.get('description')}")
            content = first.get('content', '')
            print(f"\nContent Length: {len(content)} chars")
            print(f"Content Preview: {content[:150]}...")
            
            if "chars]" in content:
                print("\n[VERDICT] Content contains truncation marker 'chars]'. It is a SNIPPET.")
            elif len(content) < 500:
                 print("\n[VERDICT] Content is very short (< 500 chars). Likely a SNIPPET or Preview.")
            else:
                 print("\n[VERDICT] Content is long. Might be full text?")
                 
except Exception as e:
    print(e)
