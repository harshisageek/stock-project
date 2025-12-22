import time
from datetime import datetime
import feedparser
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
    for domain in TRUSTED_SOURCES:
        if domain in url:
            return 1.5
    return 1.0

def fetch_google_news(ticker):
    """
    Fetches news snippets for a ticker, analyzes sentiment (FinBERT), 
    and returns weighted results. (Snippet-Only Mode)
    """
    # 1. Scrapes Google News RSS
    rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:3d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    entries = feed.entries[:10]
    
    analyzed_news = []
    total_weighted_score = 0.0
    total_weight = 0.0
    
    now = datetime.now()
    
    for entry in entries:
        # Fallback to Title + Description (Snippet)
        description = entry.description if hasattr(entry, 'description') else ""
        text_to_analyze = f"{entry.title}. {description}"
        content_source = "snippet"

        # 2. Analyze Sentiment
        raw_score = analyze_sentiment(text_to_analyze)
        
        # 3. Calculate Weights
        # Source Weight
        source_weight = calculate_source_weight(entry.link)
        
        # Recency Weight (Decay)
        try:
            pub_struct = entry.published_parsed
            pub_dt = datetime.fromtimestamp(time.mktime(pub_struct))
            hours_old = (now - pub_dt).total_seconds() / 3600
            # Decay: 1.0 at 0 hours, 0.5 at 48 hours
            recency_weight = max(0.5, 1.0 - (hours_old / 96.0)) 
        except:
            recency_weight = 1.0
            
        final_weight = source_weight * recency_weight
        
        total_weighted_score += (raw_score * final_weight)
        total_weight += final_weight
        
        analyzed_news.append({
            "title": entry.title,
            "link": entry.link,
            "publisher": entry.source.title if hasattr(entry, 'source') else "Google News",
            "published": time.strftime('%Y-%m-%d', entry.published_parsed) if hasattr(entry, 'published_parsed') else now.strftime('%Y-%m-%d'),
            "sentiment": round(raw_score, 4),
            "debug": {
                "scrape_status": "success",
                "time_taken": 0.0,
                "content_source": content_source,
                "weight": round(final_weight, 2)
            }
        })

    # Avoid division by zero
    final_sentiment = total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    return analyzed_news, final_sentiment
