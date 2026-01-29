import os
import sys
from dotenv import load_dotenv
from backend.database import NewsDatabase

load_dotenv()
db = NewsDatabase()

print("--- DB CLEANER ---")
print("Removing weak sentiment records (abs(score) < 0.05)...")

try:
    # Delete where sentiment_score < 0.05 AND sentiment_score > -0.05
    # Using parentheses for safe multi-line chaining
    query = db.client.table("news_articles").delete()
    query = query.lt("sentiment_score", 0.05)
    query = query.gt("sentiment_score", -0.05)
    
    response = query.execute()
        
    deleted_data = response.data
    count = len(deleted_data) if deleted_data else 0
    
    print(f"SUCCESS: Deleted {count} weak records.")
    
except Exception as e:
    print(f"ERROR: {e}")