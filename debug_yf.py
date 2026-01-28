
import yfinance as yf
import pandas as pd

def test_yf():
    tickers = [
        "NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NFLX", 
        "AMD", "INTC", "COIN", "MSTR", "PLTR", "HOOD", "UBER", "ABNB",
        "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"
    ]
    
    print("Downloading data...")
    try:
        # Try fetching just one first to see if it works
        data = yf.download("AAPL", period="1d", progress=False)
        print("Single ticker fetch shape:", data.shape)
        print(data.head())
        
        # Now try the group fetch
        data_group = yf.download(tickers, period="1d", group_by='ticker', progress=False)
        print("Group fetch shape:", data_group.shape)
        
        if data_group.empty:
            print("Group Data is empty!")
            return

        # Debug specific access
        print("Accessing NVDA...")
        nvda = data_group['NVDA']
        print(nvda.head())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yf()
