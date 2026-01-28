from brain.neural_networks.data_processor import DataProcessor
import logging

# Setup basic logging to see if anything is printed
logging.basicConfig(level=logging.INFO)

print("Initializing Processor...")
processor = DataProcessor()

ticker = "AAPL"
print(f"Fetching data for {ticker}...")
df = processor.fetch_stock_history(ticker)

if df is None:
    print("Fetch returned None!")
else:
    print(f"Fetch success. Rows: {len(df)}")
    print(df.head())
    
    print("Preparing ticker data...")
    result = processor.prepare_ticker_data(ticker)
    
    if result:
        xt, yt, xv, yv = result
        print(f"Success! Train: {len(xt)}, Val: {len(xv)}")
    else:
        print("Prepare returned None (likely constraints logic)")
