import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from backend.database import NewsDatabase

db = NewsDatabase()

# Clear cache for specific tickers to force fresh GNews scrape
tickers_to_clear = ["NVDA", "MSFT", "TSLA", "AAPL", "GOOGL", "AMD"]

print("--- Clearing Stale DB Records ---")
for ticker in tickers_to_clear:
    # We don't have a clear_ticker method, but we can verify what's there
    # Actually, we should just delete them.
    # Since we can't easily execute SQL directly without internal methods, 
    # we will use the supabase client directly if available, or just rely on 'test_gnews.py' logic 
    # to overwrite logic?
    
    # Wait, the app.py logic is: 
    # if cached_news: return cached_news
    # We NEED to wipe this.
    
    print(f"Clearing {ticker}...")
    try:
        # Using internal supabase client
        db.client.table("news_articles").delete().eq("ticker", ticker).execute()
        print(f"Deleted {ticker} records.")
    except Exception as e:
        print(f"Error deleting {ticker}: {e}")

print("Done. Please restart backend and search again.")
