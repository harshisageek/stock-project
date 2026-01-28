
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
# Try asking for page 2
url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&sortby=publishedAt&token={api_key}&page=2"

print(f"Requesting Page 2 from: {url.replace(api_key, 'HIDDEN')}")
try:
    resp = requests.get(url)
    data = resp.json()
    if "articles" in data:
        print(f"Received: {len(data['articles'])} articles.")
        if data['articles']:
             print(f"First Article Title: {data['articles'][0]['title']}")
    else:
        print("Error:", data)
except Exception as e:
    print(e)
