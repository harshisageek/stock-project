"""
Flask Microservice for Stock Sentiment Analysis

Provides stock price data and news sentiment analysis using Finnhub and VADER.
Implements in-memory caching with 5-minute TTL to prevent rate limiting.
"""

import sys
import os

# Add the project root to sys.path to allow importing from 'brain'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
# feedparser and vaderSentiment are now used inside brain module

from brain.quant import QuantEngine
from brain.sentiment.news import fetch_google_news, calculate_news_metrics
from backend.database import NewsDatabase

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")

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
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Cached data dict if valid, None otherwise
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
    
    Args:
        ticker: Stock ticker symbol
        data: Data to cache
    """
    cache[ticker.upper()] = {
        "data": data,
        "timestamp": time.time()
    }


def fetch_stock_data(ticker, range_str="1W"):
    # 2. Fetch News & Sentiment (Hybrid Strategy)
    # Check DB first (Fast/Full Text)
    print(f"Checking DB for {ticker}...")
    cached_news = db.get_latest_news(ticker, limit=10)
    
    if cached_news and len(cached_news) > 0:
        print(f"Found {len(cached_news)} articles in DB.")
        analyzed_news = []
        for article in cached_news:
            # Map DB format to API format
            analyzed_news.append({
                "title": article['title'],
                "published": article['published'],
                "sentiment": article['sentiment_score'],
                "link": article['link'],
                "publisher": article['source'],
                "debug": article['debug_metadata'] or {}
            })
        
        # Calculate aggregate metrics from DB data
        import numpy as np
        if analyzed_news:
            current_sentiment = np.mean([n['sentiment'] for n in analyzed_news])
        else:
            current_sentiment = 0.0
            
    else:
        # Fallback to Live Scrape (Snippet/Slow) if not in DB
        print("Not in DB. Live scraping...")
        try:
            analyzed_news, current_sentiment = fetch_google_news(ticker)
        except Exception as e:
            print(f"Error fetching news: {e}")
            analyzed_news, current_sentiment = [], 0.0

    # 3. Fetch Stock Data
    # Map range_str to Twelve Data outputsize
    range_map = {
        "1W": "7",
        "1M": "30",
        "3M": "90",
        "6M": "180",
        "1Y": "365",
        "MAX": "5000"
    }
    output_size = range_map.get(range_str, "7")

    # 2. Get Prices (Twelve Data)
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": ticker, "interval": "1day", "outputsize": output_size,
        "apikey": TWELVE_DATA_KEY
    }
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
        "price": float(d["close"]), # Keep for backward compatibility
        "sentiment": round(current_sentiment, 4)
    } for d in data["values"]]
    graph_data.reverse() # Oldest first

    # 3. Quant Brain Analysis
    engine = QuantEngine(graph_data)
    quant_result = engine.calculate_score(current_sentiment)
    
    # Derive Signal
    score = quant_result['final_score']
    if score >= 60:
        signal = "Strong Buy"
    elif score >= 20:
        signal = "Buy"
    elif score >= -20:
        signal = "Neutral"
    elif score >= -60:
        signal = "Sell"
    else:
        signal = "Strong Sell"
        
    quant_result['signal'] = signal

    # Aggregate Scraping Stats for Debugging
    scraping_stats = {
        "total": len(analyzed_news),
        "full_text": sum(1 for n in analyzed_news if n['debug']['content_source'] == 'full_text'),
        "snippet": sum(1 for n in analyzed_news if n['debug']['content_source'] == 'snippet'),
        "timeouts": sum(1 for n in analyzed_news if n['debug']['scrape_status'] == 'timeout')
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
    
    Query Parameters:
        ticker: Stock ticker symbol (required)
        
    Returns:
        JSON with current_sentiment, news, and graph_data
    """
    ticker = request.args.get("ticker")
    
    if not ticker:
        return jsonify({
            "error": "Missing required parameter: ticker"
        }), 400
    
    ticker = ticker.upper().strip()
    range_param = request.args.get("range", "1W")
    
    # Check cache first
    cache_key = f"{ticker}_{range_param}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return jsonify({
            **cached_data,
            "cached": True
        })
    
    # Fetch fresh data
    try:
        data = fetch_stock_data(ticker, range_param)
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
            "current_sentiment": 0.42,
            "news": [
                {"title": "Market resilient despite volatility", "sentiment": 0.6},
                {"title": "Analysts eye key resistance levels", "sentiment": 0.3}
            ],
            "graph_data": [
                {"date": "2023-11-01", "price": 150.00, "sentiment": 0.1},
                {"date": "2023-11-02", "price": 155.50, "sentiment": 0.4},
                {"date": "2023-11-03", "price": 153.20, "sentiment": 0.2},
                {"date": "2023-11-04", "price": 160.00, "sentiment": 0.8},
                {"date": "2023-11-05", "price": 158.00, "sentiment": 0.5}
            ],
            "circuit_breaker": True,
            "quant_analysis": {
                "final_score": 0,
                "signal": "Neutral (Circuit Breaker)",
                "breakdown": {
                    "rsi_val": 50.0,
                    "sma_val": 150.0,
                    "macd": {
                        "macd_line": 0,
                        "signal_line": 0,
                        "histogram": 0
                    }
                }
            },
            "debug": {
                "total": 0,
                "full_text": 0,
                "snippet": 0,
                "timeouts": 0
            }
        }
        return jsonify(circuit_breaker_data)


@app.route("/api/search", methods=["GET"])
def search_symbols():
    """
    Search for stock symbols using Twelve Data.
    
    Query Parameters:
        q: Search query (e.g., "AAPL" or "Apple")
        
    Returns:
        JSON list of matching symbols.
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
        
        # Twelve Data returns {"data": [...]} OR {"code": 400, ...}
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
    app.run(host="0.0.0.0", port=port, debug=debug)
