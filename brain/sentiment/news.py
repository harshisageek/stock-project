import time
from datetime import datetime, timedelta
import feedparser
from brain.sentiment.analyzer import analyze_sentiment
from brain.sentiment.scraper import scrape_articles_parallel, calculate_source_weight

def fetch_google_news(ticker):
    """
    Fetches news for a ticker, scrapes full content (parallel), 
    analyzes sentiment (FinBERT), and returns weighted results.
    """
    # 1. Scrapes Google News RSS
    rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:3d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    entries = feed.entries[:10]
    articles_to_scrape = [{"link": entry.link} for entry in entries]
    
    # 2. Parallel Scraping (Fast, with timeouts)
    scrape_results = scrape_articles_parallel(articles_to_scrape, timeout=4.5)
    
    analyzed_news = []
    total_weighted_score = 0.0
    total_weight = 0.0
    
    now = datetime.now()
    
    for i, entry in enumerate(entries):
        scrape_result = scrape_results[i]
        
        # Determine content source
        if scrape_result['status'] == 'success' and scrape_result['text']:
            text_to_analyze = scrape_result['text']
            content_source = "full_text"
        else:
            # Fallback to Title + Description
            description = entry.description if hasattr(entry, 'description') else ""
            text_to_analyze = f"{entry.title}. {description}"
            content_source = "snippet"

        # 3. Analyze Sentiment
        raw_score = analyze_sentiment(text_to_analyze)
        
        # 4. Calculate Weights
        # Source Weight
        source_weight = calculate_source_weight(entry.link)
        
        # Recency Weight (Decay)
        # Parse published date
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
                "scrape_status": scrape_result['status'],
                "time_taken": scrape_result['time_taken'],
                "content_source": content_source,
                "weight": round(final_weight, 2)
            }
        })

    # Avoid division by zero
    final_sentiment = total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    return analyzed_news, final_sentiment
