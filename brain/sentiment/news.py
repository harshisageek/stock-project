import os
import requests
import time
from datetime import datetime, timedelta
import re
import random
from brain.sentiment.analyzer import analyze_sentiment

# Trusted sources for simple weighting
TRUSTED_SOURCES = [
    "bloomberg.com", "reuters.com", "cnbc.com", "wsj.com", "ft.com", 
    "finance.yahoo.com", "marketwatch.com", "seekingalpha.com", "investing.com"
]

def calculate_source_weight(url):
    """
    Get weight (0.5 to 1.5) based on domain authority.
    """
    if not url: return 1.0
    for domain in TRUSTED_SOURCES:
        if domain in url:
            return 1.5
    return 1.0

def generate_mock_news(ticker):
    """
    Generates fallback mock news for demonstration when API keys are exhausted.
    """
    print(f"[GNews] All keys exhausted. Generating MOCK news for {ticker} to demonstrate UI.")
    
    mock_templates = [
        (f"{ticker} Reports Strong Q3 Earnings, Beating Estimates", 0.8, "Reuters"),
        (f"Analysts Upgrade {ticker} to Buy Following Tech Event", 0.6, "Bloomberg"),
        (f"Market Volatility Impacts {ticker} Share Price", -0.2, "CNBC"),
        (f"{ticker} Announces New Strategic Partnership in AI Sector", 0.9, "TechCrunch"),
        (f"Regulatory Scrutiny Increases for {ticker} in EU", -0.5, "WSJ"),
        (f"Why {ticker} Could Be the Next Trillion Dollar Company", 0.7, "Motley Fool"),
        (f"Institutions Are Loading Up on {ticker} Stock", 0.5, "Seeking Alpha"),
        (f"Short Interest in {ticker} Spikes Amid Uncertainty", -0.4, "MarketWatch"),
        (f"{ticker} CEO Discusses Future Roadmap in Interview", 0.3, "Forbes"),
        (f"New Product Launch from {ticker} Receives Mixed Reviews", -0.1, "The Verge")
    ]
    
    mock_articles = []
    now = datetime.now()
    
    for i, (title, base_sentiment, source) in enumerate(mock_templates):
        # Add some randomness to sentiment
        sentiment = base_sentiment + (random.random() * 0.1 - 0.05)
        
        mock_articles.append({
            "title": title,
            "link": f"https://example.com/mock/{ticker}/{i}",
            "image": "https://images.unsplash.com/photo-1611974765270-ca1258634369?q=80&w=500&auto=format&fit=crop",
            "publisher": source,
            "published": (now - timedelta(hours=i*2)).strftime('%Y-%m-%d'),
            "sentiment": round(sentiment, 4),
            "debug": {
                "source": "Mock/Demo",
                "content_source": "fallback_generator",
                "key_used": "None",
                "weight": 1.0,
                "raw_title_score": round(base_sentiment, 4)
            }
        })
        
    return mock_articles, 0.45 # Return positive avg sentiment

def fetch_gnews(ticker, company_name=None):
    """
    Fetches news using GNews API with Dual-Key Rotation.
    Analyzes sentiment primarily based on TITLE (60%) and DESCRIPTION (40%).
    Ignores truncated content to avoid dilution.
    """
    keys = [
        os.getenv("GNEWS_API_KEY1"),
        os.getenv("GNEWS_API_KEY2")
    ]
    
    # Filter out None keys
    keys = [k for k in keys if k]
    
    if not keys:
        print("[GNews] No API Keys found!")
        return generate_mock_news(ticker)

    valid_articles = []
    seen_titles = set()
    now = datetime.now()
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    # Fetch Loop: Keep fetching pages until we have 20 valid articles or hit Page 4
    current_key_idx = 0
    max_pages = 4 # Safety limit to prevent burning credits
    target_count = 20
    
    keys_exhausted = False
    
    for page in range(1, max_pages + 1):
        if len(valid_articles) >= target_count:
            break
            
        print(f"[GNews] Fetching Page {page}... (Current Valid: {len(valid_articles)})")
        
        # If we ran out of keys, stop
        if current_key_idx >= len(keys):
            keys_exhausted = True
            break
            
        page_articles = []
        success = False
        
        # Try current key, if fail, rotate
        while current_key_idx < len(keys):
            key = keys[current_key_idx]
            try:
                # Refine Search Query to avoid "Spy movies" or "Move dance"
                search_query = ticker
                
                # Priority: Use Company Name if available
                if company_name:
                    # Clean up common suffixes
                    clean_name = re.sub(r' (Inc\.?|Corp\.?|Corporation|Ltd\.?|PLC|S\.A\.|AG|L\.P\.|Holdings)\b', '', company_name, flags=re.IGNORECASE).strip()
                    search_query = f"{ticker} {clean_name} stock"
                
                # Fallback: Smart Guessing
                else:
                    # Crypto
                    if "USD" in ticker:
                        search_query = ticker.replace("-", " ")
                    # ETFs
                    elif ticker in ["SPY", "QQQ", "IWM", "DIA", "VXX", "IVV", "VOO"]:
                        search_query = f"{ticker} ETF"
                    # Ambiguous / Short Tickers
                    elif len(ticker) <= 4 or ticker in ["MOVE", "BEST", "FAST", "NOW", "LOVE", "CASH", "LUV", "MAIN", "PLAY"]:
                        search_query = f"{ticker} stock"
                
                # Encode spaces? Requests handles it, but f-string is safe
                url = f"https://gnews.io/api/v4/search?q={search_query}&lang=en&sortby=publishedAt&token={key}&page={page}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "articles" in data:
                        page_articles = data["articles"]
                    success = True
                    break 
                    
                elif response.status_code == 429: # Rate Limit
                    print(f"[GNews] Key #{current_key_idx+1} Rate Limited. Switching...")
                    current_key_idx += 1 
                    continue
                elif response.status_code == 403: # Quota
                    print(f"[GNews] Key #{current_key_idx+1} Forbidden (Quota). Switching...")
                    current_key_idx += 1
                    continue
                else:
                    print(f"[GNews] Key #{current_key_idx+1} Error: {response.status_code}")
                    current_key_idx += 1
                    continue
                    
            except Exception as e:
                print(f"[GNews] Exception: {e}")
                current_key_idx += 1
                continue
        
        if not success:
            print(f"[GNews] Failed to fetch page {page}. Stopping.")
            if current_key_idx >= len(keys):
                keys_exhausted = True
            break
            
        # Process this page's articles immediately to check validity
        for article in page_articles:
            if len(valid_articles) >= target_count:
                break
                
            title = article.get('title', '')
            if title in seen_titles:
                continue
            
            # 1. Analyze Sentiment
            desc = article.get('description', '')
            score_title = analyze_sentiment(title)
            
            # Weighted Average: Title (50%), Desc (50%) - Reduced Title influence
            if desc and len(desc) > 10:
                 score_desc = analyze_sentiment(desc)
                 sentiment_score = (score_title * 0.5) + (score_desc * 0.5)
            else:
                 sentiment_score = score_title
            
            # Dampening: Pull towards neutral to avoid extreme 0.99s
            sentiment_score = sentiment_score * 0.85

            # 2. FILTER NEUTRALS (Strict)
            # User wants to discard 0.00 scores completely
            if abs(sentiment_score) < 0.05:
                # Debug print to see what's being dropped
                print(f"[News Filter] Dropping '{title}' (Score: {sentiment_score:.4f})")
                continue
                
            seen_titles.add(title)
            
            # 3. Add to List
            source_url = article.get('url', '')
            source_weight = calculate_source_weight(source_url)
            
            # Recency
            try:
                pub_date = article.get('publishedAt')
                if pub_date:
                    dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    hours_old = (now - dt).total_seconds() / 3600
                    recency_weight = max(0.5, 1.0 - (hours_old / 96.0))
                    pub_str = dt.strftime('%Y-%m-%d')
                else:
                    recency_weight = 1.0
                    pub_str = now.strftime('%Y-%m-%d')
            except:
                recency_weight = 1.0
                pub_str = now.strftime('%Y-%m-%d')
                
            final_weight = source_weight * recency_weight
            
            total_weighted_score += (sentiment_score * final_weight)
            total_weight += final_weight
            
            valid_articles.append({
                "title": title,
                "link": source_url,
                "image": article.get('image', ''),
                "publisher": article.get('source', {}).get('name', 'GNews'),
                "published": pub_str,
                "sentiment": round(sentiment_score, 4),
                "debug": {
                    "source": "GNews",
                    "content_source": "filtered_loop",
                    "key_used": "Multi-Page",
                    "weight": round(final_weight, 2),
                    "raw_title_score": round(score_title, 4)
                }
            })
    
    # Check if we should fallback to mock data
    if len(valid_articles) == 0 and keys_exhausted:
        print("[GNews] CRITICAL: All keys exhausted and no articles found. Falling back to MOCK data.")
        return generate_mock_news(ticker)

    if len(valid_articles) < target_count:
        print(f"[GNews] Warning: Only found {len(valid_articles)} valid articles after {max_pages} pages.")
        
    print(f"[GNews] Final Valid Articles: {len(valid_articles)}")
    
    final_sentiment = total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    return valid_articles, final_sentiment