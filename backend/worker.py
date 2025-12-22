import time
import os
from backend.database import NewsDatabase
from brain.sentiment.analyzer import analyze_sentiment
import feedparser

# Top 150 Stocks (Approximation of "Active" S&P 500)
TOP_150_STOCKS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK.B", "LLY", "AVGO",
    "JPM", "V", "UNH", "WMT", "MA", "XOM", "PG", "HD", "JNJ", "ORCL",
    "COST", "ABBV", "BAC", "KO", "CRM", "NFLX", "AMD", "PEP", "CVX", "TMO",
    "WFC", "LIN", "CSCO", "MCD", "ADBE", "ACN", "DIS", "ABT", "TMUS", "DHR",
    "GE", "INTU", "VZ", "QCOM", "CAT", "IBM", "AMAT", "NOW", "PFE", "UBER", 
    "TXN", "MS", "CMCSA", "ISRG", "PM", "AXP", "GS", "UNP", "SPGI", "LOW",
    "RTX", "HON", "COP", "BKNG", "PLD", "BLK", "SYK", "ETN", "PANW", "TJX",
    "PGR", "C", "LRCX", "VRTX", "ELV", "REGN", "MDLZ", "ADP", "MMC", "BSX",
    "ADI", "DE", "CI", "LMT", "CB", "GILD", "MU", "AMT", "SCHW", "BA",
    "NEE", "FI", "BX", "EQIX", "KLAC", "SNPS", "ZTS", "WM", "MO", "CDNS",
    "CME", "SHW", "ITW", "SO", "ICE", "BDX", "CSX", "CL", "TGT", "DUK",
    "MCK", "PH", "EOG", "SLB", "TDG", "NOC", "PSX", "MAR", "APH", "ORLY",
    "USB", "EMR", "PyPL", "GD", "NXPI", "HCA", "AON", "PCAR", "MCO", "FDX",
    "APD", "ECL", "CTAS", "ROP", "PNC", "COF", "FCX", "MMM", "NSC", "GM" 
]

def worker_main():
    print(f"--- STARTING CLOUD WORKER (SNIPPET MODE) ---", flush=True)
    print(f"Target: {len(TOP_150_STOCKS)} Stocks", flush=True)
    
    db = NewsDatabase()
    
    total_processed = 0
    total_articles = 0
    
    for ticker in TOP_150_STOCKS:
        # Using Google News RSS (Snippet) as Discovery Source
        rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:1d&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        # Limit to 30 snippets per stock to avoid clutter but get good coverage
        entries = feed.entries[:30]
        
        print(f"[{ticker}] Processing {len(entries)} snippets...", flush=True)
        
        for entry in entries:
            link = entry.link
            title = entry.title
            summary = entry.summary if hasattr(entry, 'summary') else ""
            
            # Combine Title + Summary for Analysis
            text_to_analyze = f"{title}. {summary}"
            
            # --- AI ANALYSIS ---
            sentiment = analyze_sentiment(text_to_analyze)
            
            # --- SAVE TO DB ---
            article_data = {
                "link": link,
                "title": title,
                "published": time.strftime('%Y-%m-%d', entry.published_parsed) if hasattr(entry, 'published_parsed') else "",
                "publisher": entry.source.title if hasattr(entry, 'source') else "Google News",
                "text": None, # No full text in snippet mode
                "snippet": summary[:1000],
                "sentiment": sentiment,
                "debug": {
                    "source": "snippet",
                    "worker_version": "2.0 (Snippet Only)"
                }
            }
            
            db.upsert_article(ticker, None, article_data)
            total_articles += 1
            
        total_processed += 1
        # Minimal sleep just to be polite to Google RSS
        time.sleep(0.1)
        
    print(f"--- WORKER COMPLETE ---")
    print(f"Stocks Scanned: {total_processed}")
    print(f"Articles Saved: {total_articles}")

if __name__ == "__main__":
    worker_main()
