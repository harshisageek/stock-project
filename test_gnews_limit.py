
import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("GNEWS_API_KEY1")

if not api_key:
    print("No GNEWS_API_KEY1")
    sys.exit(1)

ticker = "AAPL"
# Try asking for 20
url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&sortby=publishedAt&max=20&token={api_key}"

print(f"Requesting 20 articles from: {url.replace(api_key, 'HIDDEN')}")
try:
    resp = requests.get(url)
    data = resp.json()
    if "articles" in data:
        print(f"Received: {len(data['articles'])} articles.")
    else:
        print("Error:", data)
except Exception as e:
    print(e)
