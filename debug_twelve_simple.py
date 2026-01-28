import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TWELVE_DATA_KEY")
print(f"API Key present: {bool(api_key)}")

ticker = "AAPL"
url = "https://api.twelvedata.com/time_series"
params = {"symbol": ticker, "interval": "1day", "outputsize": "5000", "apikey": api_key} # Match DataProcessor

try:
    response = requests.get(url, params=params)
    data = response.json()
    if "values" in data:
        print("Success! Got values.")
        print(f"Count: {len(data['values'])}")
    else:
        print("Failed.")
        print(f"Response: {data}")
except Exception as e:
    print(f"Exception: {e}")
