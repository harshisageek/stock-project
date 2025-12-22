import yfinance as yf
try:
    print("Attempting to fetch AAPL...")
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1mo") # Short period for quick check
    if hist.empty:
        print("Empty DataFrame returned.")
    else:
        print("Success! Data fetched.")
        print(hist.head())
except Exception as e:
    print(f"yfinance failed: {e}")
