import time
from datetime import datetime
import feedparser
from brain.sentiment.analyzer import analyze_sentiment

def fetch_google_news(ticker):
    # Scrapes Google News RSS (Free, No Auth)
    rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:3d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    analyzed_news = []
    total_sentiment = 0.0
    count = 0
    for entry in feed.entries[:10]:
        clean_title = entry.title.split(" - ")[0]
        score = analyze_sentiment(clean_title)
        total_sentiment += score
        count += 1
        analyzed_news.append({
            "title": clean_title,
            "published": time.strftime('%Y-%m-%d', entry.published_parsed) if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d'),
            "sentiment": round(score, 4),
            "link": entry.link,
            "publisher": entry.source.title if hasattr(entry, 'source') else "Google News"
        })
    return analyzed_news, (total_sentiment / count if count > 0 else 0.0)
