
"""
Flask Microservice for Stock Sentiment Analysis

Provides stock price data and news sentiment analysis using GNews (Dual-Key) and FinBERT.
Implements in-memory caching with 5-minute TTL to prevent rate limiting.
"""

import sys
import os
import threading

# Add the project root to sys.path to allow importing from 'brain'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from brain.quant import QuantEngine
# Import new GNews fetcher
from brain.sentiment.news import fetch_gnews
from backend.database import NewsDatabase

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, requests.exceptions.HTTPError):
        return jsonify({"error": str(e)}), e.response.status_code
    
    # Generic Error
    return jsonify({"error": str(e)}), 500

# Twelve Data API Key
TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")
if not TWELVE_DATA_KEY:
    print("Warning: TWELVE_DATA_KEY not found in environment variables.")

# Initialize DB
db = NewsDatabase()

# In-memory cache: {ticker: {"data": {...}, "timestamp": float}}
cache = {}
CACHE_TTL_SECONDS = 5 * 60  # 5 minutes


def get_cached_data(ticker: str) -> dict | None:
    """
    Retrieve cached data for a ticker if it exists and is not expired.
    """
    ticker_upper = ticker.upper()
    if ticker_upper in cache:
        cached_entry = cache[ticker_upper]
        age = time.time() - cached_entry["timestamp"]
        if age < CACHE_TTL_SECONDS:
            return cached_entry["data"]
    return None


def set_cached_data(ticker: str, data: dict) -> None:
    """
    Store data in cache with current timestamp.
    """
    cache[ticker.upper()] = {
        "data": data,
        "timestamp": time.time()
    }

def update_news_background(ticker):
    """
    Fetches GNews in the background and updates DB.
    """
    print(f"[Background] Updating news for {ticker} using GNews...")
    try:
        analyzed_news, current_sentiment = fetch_gnews(ticker)
        
        if analyzed_news:
            print(f"[Background] Found {len(analyzed_news)} articles. Saving to DB...")
            # Save to DB
            for article in analyzed_news:
                # DB schema expects slightly different keys, but upsert_article handles most.
                # Just need to make sure 'link' is present (which it is).
                db.upsert_article(ticker, None, article)
        else:
            print("[Background] No news found.")
            
    except Exception as e:
        print(f"[Background] Update Failed: {e}")



from backend.manager import model_manager

# ... (Imports) Note: I'm replacing the whole file's critical sections, so I'll do this in chunks.
# Actually, I'll use replace_file_content to swap specific blocks to be safe.

def fetch_stock_data(ticker, range_str="1W", force_refresh=False, company_name=None):
    # 2. Fetch News & Sentiment
    print(f"Checking DB for {ticker}...")
    
    analyzed_news = []
    cached_news = []

    # If NOT forcing refresh, try to get from DB
    if not force_refresh:
        cached_news = db.get_latest_news(ticker, limit=20)
    else:
        print("[Force Refresh] Skipping DB cache.")
    
    should_fetch_live = False
    
    if cached_news and len(cached_news) >= 5: # Lower threshold to 5 for now
        print(f"Found {len(cached_news)} articles in DB. (Cache Hit)")
        for article in cached_news:
            analyzed_news.append({
                "title": article['title'],
                "published": article['published'],
                "sentiment": article['sentiment_score'],
                "link": article['link'],
                "publisher": article['source'],
                "debug": article['debug_metadata'] or {}
            })
            
        # Trigger background update to keep data fresh (optional, maybe only if old?)
        # For now, let's trust the DB if we hit it, unless user forces refresh.
        
    else:
        # DB Empty or Force Refresh - Must Fetch Live (Blocking)
        print("DB Empty or Forced. Live scraping (Blocking)...")
        
        # Pass company name to refine search
        analyzed_news, _ = fetch_gnews(ticker, company_name)
        
        # Save immediately
        for article in analyzed_news:
             db.upsert_article(ticker, None, article)

    # Calculate Weighted Sentiment
    if analyzed_news:
        total_weighted_score = 0.0
        total_weights = 0.0
        for n in analyzed_news:
            weight = n['debug'].get('weight', 1.0)
            total_weighted_score += (n['sentiment'] * weight)
            total_weights += weight
        current_sentiment = total_weighted_score / total_weights if total_weights > 0 else 0.0
    else:
        current_sentiment = 0.0

    # 3. Fetch Stock Data (Twelve Data)
    range_map = {"1W": "7", "1M": "30", "3M": "90", "6M": "180", "1Y": "365", "MAX": "5000"}
    output_size = range_map.get(range_str, "7")

    url = "https://api.twelvedata.com/time_series"
    params = {"symbol": ticker, "interval": "1day", "outputsize": output_size, "apikey": TWELVE_DATA_KEY}
    
    response = requests.get(url, params=params)
    data = response.json()

    if "values" not in data:
        raise ValueError(f"Twelve Data Error: {data.get('message', 'Unknown error')}")

    graph_data = [{
        "date": d["datetime"],
        "open": float(d["open"]),
        "high": float(d["high"]),
        "low": float(d["low"]),
        "close": float(d["close"]),
        "volume": int(d["volume"]),
        "price": float(d["close"]),
        "sentiment": round(current_sentiment, 4)
    } for d in data["values"]]
    graph_data.reverse() # Oldest first

    # 3. Quant Brain Analysis (Rule-Based)
    engine = QuantEngine(graph_data)
    quant_result = engine.calculate_score(current_sentiment)
    
    # 4. Neural Network Analysis (AI Prediction) via Manager
    neural_signal, neural_confidence = model_manager.predict_sentiment(graph_data)

    # Derive Combined Signal
    score = quant_result['final_score']
    
    # Quant Signals
    if score >= 60: quant_signal = "Strong Buy"
    elif score >= 20: quant_signal = "Buy"
    elif score >= -20: quant_signal = "Neutral"
    elif score >= -60: quant_signal = "Sell"
    else: quant_signal = "Strong Sell"
        
    quant_result['signal'] = quant_signal
    
    # Add Neural Info
    quant_result['neural_analysis'] = {
        "signal": neural_signal,
        "confidence": round(neural_confidence, 4),
        "model": "Hybrid LSTM v1 (Optimized)"
    }
    
    # Debug Stats
    scraping_stats = {
        "total": len(analyzed_news),
        "full_text": sum(1 for n in analyzed_news if n['debug'].get('content_source') == 'full_text'),
        "snippet": sum(1 for n in analyzed_news if n['debug'].get('content_source') != 'full_text'),
        "timeouts": 0
    }
    
    return {
        "current_sentiment": round(current_sentiment, 4),
        "news": analyzed_news,
        "graph_data": graph_data,
        "quant_analysis": quant_result,
        "debug": scraping_stats
    }


@app.route("/api/analyze", methods=["GET"])
def analyze():
    """
    Analyze stock sentiment for a given ticker.
    """
    ticker = request.args.get("ticker")
    
    if not ticker:
        return jsonify({
            "error": "Missing required parameter: ticker"
        }), 400
    
    ticker = ticker.upper().strip()
    range_param = request.args.get("range", "1W")
    force_refresh = request.args.get("force", "false").lower() == "true"
    company_name = request.args.get("name") # Optional company name from frontend
    
    # Check cache first (skip if forcing refresh)
    cache_key = f"{ticker}_{range_param}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data and not force_refresh:
        return jsonify({
            **cached_data,
            "cached": True
        })
    
    # Fetch fresh data
    try:
        data = fetch_stock_data(ticker, range_param, force_refresh=force_refresh, company_name=company_name)
        set_cached_data(cache_key, data)
        return jsonify({
            **data,
            "cached": False
        })
    except Exception as e:
        # Circuit Breaker: Log error and return mock data for frontend rendering
        print(f"Warning: Data provider blocked or failed. Switching to Circuit Breaker. Error: {e}")
        
        circuit_breaker_data = {
            "ticker": ticker,
            "current_sentiment": 0.0,
            "news": [],
            "graph_data": [],
            "circuit_breaker": True,
            "error": str(e)
        }
        return jsonify(circuit_breaker_data)


import threading


import time


import schedule


from bs4 import BeautifulSoup





# ... (Previous imports and setup remain, I will preserve them via context if I could, but 'replace' needs exact context. 


# Since I am replacing the specific cache/route sections, I will target the bottom half of the file where market_movers and general_news are.)





# --- CACHE STORAGE ---


movers_cache = {


    "data": {"gainers": [], "losers": [], "active": []},


    "timestamp": 0


}





news_cache = {
    "data": [],
    "timestamp": 0
}





# --- BACKGROUND WORKERS ---





def update_movers_cache():


    """Scrapes StockAnalysis.com and updates the global cache."""


    global movers_cache


    print("[Scheduler] Updating Market Movers...")


    


    def scrape_category(endpoint):


        base_url = "https://stockanalysis.com/markets"


        url = f"{base_url}/{endpoint}/"


        headers = {


            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


        }


        


        try:


            res = requests.get(url, headers=headers, timeout=10)


            if res.status_code != 200:


                print(f"[Scraper] Failed {endpoint}: {res.status_code}")


                return []


                


            soup = BeautifulSoup(res.text, 'html.parser')


            table = soup.find('table')


            if not table: return []


            


            rows = table.find_all('tr')[1:6] # Top 5


            data = []


            


            for row in rows:


                cols = row.find_all('td')


                if len(cols) < 5: continue


                


                try:


                    symbol = cols[1].get_text(strip=True)


                    name = cols[2].get_text(strip=True)


                    price = cols[3].get_text(strip=True)


                    change_pct = cols[5].get_text(strip=True).replace('%', '')


                    volume_str = cols[-2].get_text(strip=True) if len(cols) >= 7 else "0"


                    


                    data.append({


                        "symbol": symbol,


                        "name": name,


                        "price": f"${price}",


                        "change": float(change_pct.replace(',', '')),


                        "raw_change": float(change_pct.replace(',', '')),


                        "volume_fmt": volume_str


                    })


                except Exception as ex:


                    continue


            return data


            


        except Exception as e:


            print(f"[Scraper] Error {endpoint}: {e}")


            return []





    gainers = scrape_category("gainers")


    losers = scrape_category("losers")


    active = scrape_category("active")


    


    if gainers or losers:


        movers_cache["data"] = {


            "gainers": gainers,


            "losers": losers,


            "active": active


        }


        movers_cache["timestamp"] = time.time()


        print("[Scheduler] Market Movers Updated.")





def update_news_cache():
    """Fetches GNews 'stock market' and updates global cache."""
    global news_cache
    print("[Scheduler] Updating General News...")
    
    try:
        articles, _ = fetch_gnews("stock market")
        top_news = articles[:15]
        
        if top_news:
            news_cache["data"] = top_news
            news_cache["timestamp"] = time.time()
            print("[Scheduler] General News Updated.")
            
    except Exception as e:
        print(f"[Scheduler] News Update Error: {e}")





def run_scheduler():


    """Background loop to run updates every 2 hours."""


    # Initial run


    update_movers_cache()


    update_news_cache()


    


    # Schedule


    schedule.every(2).hours.do(update_movers_cache)


    schedule.every(2).hours.do(update_news_cache)


    


    while True:


        schedule.run_pending()


        time.sleep(60)





def start_background_scheduler():


    """Starts the scheduler in a daemon thread."""


    import schedule # Ensure schedule is imported or available


    thread = threading.Thread(target=run_scheduler, daemon=True)


    thread.start()





# --- API ENDPOINTS ---





@app.route("/api/market-movers", methods=["GET"])





def market_movers():





    """Returns cached market movers (auto-refreshed in bg)."""





    # Non-blocking: If cache is empty, return empty structure immediately





    # The background scheduler (start_background_scheduler) handles the update





    return jsonify(movers_cache["data"])





@app.route("/api/general-news", methods=["GET"])
def general_news():
    """Returns cached general news (auto-refreshed in bg)."""
    force = request.args.get('force', 'false').lower() == 'true'
    
    if force or not news_cache["data"]:
        update_news_cache()
        
    return jsonify(news_cache["data"])





@app.route("/api/search", methods=["GET"])
def search_symbols():
    """
    Search for stock symbols using Twelve Data.
    """
    query = request.args.get("q")
    if not query:
        return jsonify({"data": []})
        
    url = "https://api.twelvedata.com/symbol_search"
    params = {
        "symbol": query,
        "apikey": TWELVE_DATA_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "data" in data:
            return jsonify(data)
        else:
            return jsonify({"data": []})
            
    except Exception as e:
        print(f"Search API Error: {e}")
        return jsonify({"data": []})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Start Background Workers
    start_background_scheduler()
    
    app.run(host="0.0.0.0", port=port, debug=debug)
