
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("TWELVE_DATA_KEY")

def test_twelve():
    if not KEY:
        print("Error: No API Key found in .env")
        return

    symbols = ["AAPL", "NVDA", "BTC/USD"]
    symbol_str = ",".join(symbols)
    
    url = "https://api.twelvedata.com/quote"
    params = {
        "symbol": symbol_str,
        "apikey": KEY
    }
    
    print(f"Fetching: {url}?symbol={symbol_str}&apikey=HIDDEN")
    
    try:
        res = requests.get(url, params=params)
        print(f"Status: {res.status_code}")
        
        data = res.json()
        print("Response Data:")
        print(data)
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_twelve()
