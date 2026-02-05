import os
import requests
import re
import random
import logging
from datetime import datetime, timedelta
# Use New Industry-Grade Engine
from brain.analysis.sentiment import SentimentEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TRUSTED_SOURCES = [
    "bloomberg.com", "reuters.com", "cnbc.com", "wsj.com", "ft.com", 
    "finance.yahoo.com", "marketwatch.com", "seekingalpha.com", "investing.com",
    "barrons.com", "forbes.com", "businessinsider.com"
]

# Track dead keys in memory (Global state for the running process)
_BAD_KEYS = set()

def calculate_source_weight(url: str) -> float:
    """
    Returns a weight multiplier (1.0 to 1.5) based on domain authority.
    """
    if not url: return 1.0
    
    url_lower = url.lower()
    for domain in TRUSTED_SOURCES:
        if domain in url_lower:
            return 1.5
    return 1.0

def generate_mock_news(ticker: str) -> tuple[list, float]:
    """
    Generates realistic mock news when API limits are hit.
    """
    logger.warning(f"[Mock] Generating fallback news for {ticker} (API Limits/Errors).")
    
    templates = [
        ("Reports Strong Quarterly Earnings", 0.8, "Reuters"),
        ("Analyst Upgrade: Buy Rating Issued", 0.7, "Bloomberg"),
        ("Market Volatility Concerns Affect Price", -0.3, "CNBC"),
        ("New Strategic Partnership Announced", 0.85, "Business Wire"),
        ("Regulatory Challenges Ahead", -0.6, "WSJ"),
        ("Why This Stock Is A Top Pick", 0.65, "Motley Fool"),
        ("Institutional Investors Increase Stake", 0.5, "Seeking Alpha"),
        ("Short Interest Spikes", -0.45, "MarketWatch"),
        ("CEO Interview: Future Roadmap", 0.4, "Forbes"),
        ("Tech Sector Sell-Off Impacts Stock", -0.5, "The Verge")
    ]
    
    mock_articles = []
    now = datetime.now()
    
    for i, (headline_suffix, base_score, source) in enumerate(templates):
        # Randomize slightly
        sentiment = base_score + (random.uniform(-0.1, 0.1))
        # Dampen mock scores too for consistency
        sentiment = sentiment * 0.95
        
        # Clear indication of Mock Data
        title = f"[API FAILED - MOCK DATA] {ticker} {headline_suffix}"
        
        mock_articles.append({
            "title": title,
            "link": f"https://mock-news.com/{ticker}/{i}",
            "image": "https://via.placeholder.com/150?text=News",
            "publisher": source,
            "published": (now - timedelta(hours=i*4)).strftime('%Y-%m-%d'),
            "sentiment": round(sentiment, 4),
            "debug": {
                "source": "Mock/Fallback",
                "weight": 1.0,
                "raw_score": round(base_score, 4)
            }
        })
        
    # Mock Average Sentiment
    avg_sentiment = 0.35
    return mock_articles, avg_sentiment

def fetch_gnews(ticker: str, company_name: str = None) -> tuple[list, float]:
    """
    Fetches news from GNews API with strict credit conservation.
    Uses new SentimentEngine.
    """
    global _BAD_KEYS
    
    keys = [os.getenv("GNEWS_API_KEY1"), os.getenv("GNEWS_API_KEY2")]
    active_keys = [k for k in keys if k and k not in _BAD_KEYS]
    
    if not active_keys:
        logger.error("No active GNews keys available.")
        return generate_mock_news(ticker)

    # Search Query Optimization
    if company_name:
        clean_name = re.sub(r' (Inc\.?|Corp\.?|Corporation|Ltd\.?|PLC|S\.A\.|AG)\b', '', company_name, flags=re.IGNORECASE).strip()
        search_query = f'"{clean_name}" OR "{ticker} stock"'
    else:
        if len(ticker) <= 4:
            search_query = f'"{ticker} stock"'
        else:
            search_query = ticker

    valid_articles = []
    seen_titles = set()
    now = datetime.now()
    
    target_count = 20
    max_pages = 5 # Increased to 5 to ensure 20 valid articles after strict filtering
    
    current_key_idx = 0
    
    for page in range(1, max_pages + 1):
        if len(valid_articles) >= target_count:
            break
            
        response_data = None
        
        # Retry loop for keys
        while current_key_idx < len(active_keys):
            api_key = active_keys[current_key_idx]
            try:
                # Explicit max=10 (Free Tier Limit)
                url = f"https://gnews.io/api/v4/search?q={search_query}&lang=en&sortby=publishedAt&token={api_key}&page={page}&max=10"
                
                logger.info(f"Fetching GNews Page {page}...")
                res = requests.get(url, timeout=10)
                
                if res.status_code == 200:
                    response_data = res.json()
                    break 
                elif res.status_code in [403, 429]:
                    logger.warning(f"Key exhausted. Switching.")
                    _BAD_KEYS.add(api_key)
                    current_key_idx += 1 
                else:
                    logger.error(f"GNews Error {res.status_code}: {res.text}")
                    current_key_idx += 1 
            except Exception as e:
                logger.error(f"Network Error: {e}")
                current_key_idx += 1
        
        if not response_data or "articles" not in response_data:
            break
            
        articles = response_data.get("articles", [])
        if not articles:
            logger.info("No more articles found.")
            break
            
        # Process Batch
        # We process title+description.
        # To optimize, we could batch analyze, but the loop logic filters duplicates first.
        # Let's collect texts to analyze in batch for this page.
        
        candidates = []
        for art in articles:
            title = art.get('title', '')
            if not title or title in seen_titles:
                continue
            candidates.append(art)
            seen_titles.add(title)
            
        if not candidates:
            continue
            
        # Batch Analysis
        texts = [f"{c.get('title', '')}. {c.get('description', '') or ''}" for c in candidates]
        scores = SentimentEngine.analyze_batch(texts)
        
        for art, score in zip(candidates, scores):
            if len(valid_articles) >= target_count:
                break
                
            # Filter: Reject weak signals (using the new damped score)
            # Damped score of 0.05 is still very weak.
            if abs(score) < 0.05:
                continue
                
            # Weighting
            source_url = art.get('url', '')
            source_weight = calculate_source_weight(source_url)
            
            # Recency
            try:
                pub_date = art.get('publishedAt')
                if pub_date:
                    dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    hours_old = (now - dt).total_seconds() / 3600
                    recency_weight = max(0.5, 1.0 - (hours_old / 72.0))
                    pub_str = dt.strftime('%Y-%m-%d')
                else:
                    recency_weight = 1.0
                    pub_str = now.strftime('%Y-%m-%d')
            except:
                recency_weight = 1.0
                pub_str = now.strftime('%Y-%m-%d')

            final_weight = source_weight * recency_weight

            valid_articles.append({
                "title": art.get('title', ''),
                "link": source_url,
                "image": art.get('image', ''),
                "publisher": art.get('source', {}).get('name', 'GNews'),
                "published": pub_str,
                "sentiment": score, # Already rounded/damped by engine
                "debug": {
                    "source": "GNews",
                    "weight": round(final_weight, 2),
                    "raw_score": score
                }
            })

    # Final Aggregation
    if not valid_articles:
        # Only fallback to mock if we ran out of keys or had errors
        if not active_keys or current_key_idx >= len(active_keys):
            return generate_mock_news(ticker)
        
        # If API succeeded but just found no news (e.g. obscure ticker), return empty
        logger.info(f"No valid articles found for {ticker}.")
        return [], 0.0

    # Weighted Average
    total_score = 0.0
    total_weight = 0.0
    
    for a in valid_articles:
        w = a['debug']['weight']
        s = a['sentiment']
        total_score += (s * w)
        total_weight += w
        
    final_sentiment = total_score / total_weight if total_weight > 0 else 0.0
    
    logger.info(f"Final: {len(valid_articles)} articles, Sentiment: {final_sentiment:.4f}")
    return valid_articles, final_sentiment