import os
from supabase import create_client, Client
from dotenv import load_dotenv
import time

load_dotenv()

# Supabase Credentials (from .env or GitHub Secrets)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class NewsDatabase:
    def __init__(self):
        self.client: Client = None
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("[DB] Connected to Supabase.")
            except Exception as e:
                print(f"[DB] Connection Failed: {e}")
        else:
            print("[DB] Warning: SUPABASE_URL or SUPABASE_KEY not set. Running in Dummy Mode.")

    def upsert_article(self, ticker, start_time, article_data):
        """
        Save or Update an article in the DB.
        """
        if not self.client:
            return
            
        data = {
            "ticker": ticker,
            "link": article_data['link'],
            "title": article_data['title'],
            "published": article_data.get('published'),
            "source": article_data.get('publisher'),
            "full_text": article_data.get('text', ''),
            "snippet": article_data.get('snippet', ''),
            "sentiment_score": article_data.get('sentiment', 0.0),
            "scraped_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "debug_metadata": article_data.get('debug', {})
        }
        
        try:
            # Upsert based on link (assuming link is unique constraint)
            self.client.table("news_articles").upsert(data, on_conflict="link").execute()
            # print(f"[DB] Saved: {data['title'][:30]}...")
        except Exception as e:
            print(f"[DB] Save Error: {e}")

    def get_latest_news(self, ticker, limit=10):
        """
        Fetch latest news for a ticker from DB.
        """
        if not self.client:
            return []
            
        try:
            response = self.client.table("news_articles")\
                .select("*")\
                .eq("ticker", ticker)\
                .order("published", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"[DB] Fetch Error: {e}")
            return []
