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
target = 100
url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&sortby=publishedAt&max={target}&token={api_key}"

print(f"Requesting {target} articles from API...")
try:
    resp = requests.get(url)
    data = resp.json()
    
    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {data}")
        sys.exit(1)
        
    if "articles" in data:
        count = len(data['articles'])
        print(f"Success. Received: {count} articles.")
        if count < target:
            print(f"Note: Requested {target} but API only returned {count}. This confirms the plan limit.")
    else:
        print("Response structure unexpected:", data)
except Exception as e:
    print(f"Exception: {e}")