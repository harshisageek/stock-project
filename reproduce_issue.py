
import sys
import os
import logging

# Mute logging
logging.disable(logging.CRITICAL)

# Add project root
sys.path.append(os.getcwd())

from backend.app import fetch_stock_data, db

print("--- REPRODUCING ISSUE ---")
ticker = "AAPL"

# 1. Ensure DB has data (we saw it does in debug_db_sentiment.py)
# 2. Call fetch_stock_data in "Cache Mode" (force_refresh=False)
try:
    print(f"Calling fetch_stock_data('{ticker}', force_refresh=False)...")
    result = fetch_stock_data(ticker, force_refresh=False)
    
    news = result.get('news', [])
    print(f"Returned {len(news)} articles.")
    
    failed_count = 0
    for i, art in enumerate(news):
        s = art.get('sentiment', 0.0)
        title = art.get('title', 'No Title')[:20]
        
        if abs(s) < 0.05:
            print(f"FAIL: Found weak article! Score: {s} - {title}...")
            failed_count += 1
        else:
            # print(f"PASS: Score: {s}")
            pass
            
    if failed_count > 0:
        print(f"TEST FAILED: {failed_count} weak articles returned.")
    else:
        print("TEST PASSED: No weak articles returned.")
        
except Exception as e:
    print(f"CRASH: {e}")
