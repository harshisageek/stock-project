import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.database import NewsDatabase
from brain.sentiment.analyzer import analyze_sentiment

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

def setup_driver():
    """Setup Headless Chrome for GitHub Actions Env"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    chrome_options.page_load_strategy = 'eager' # Don't wait for images/css
    
    # In GitHub Actions, usually Chrome is installed. Local fallback for dev.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(10) # Strict timeout
    return driver

def scrape_full_text(driver, url, timeout=10):
    try:
        # Strict defensive check
        driver.set_page_load_timeout(timeout)
        print(f"Scraping: {url[:100]}...", flush=True) # Log URL to identify hanging sites
        
        driver.get(url)
        
        # Reduced sleep: We are hitting different publishers, so we don't need long sleeps.
        # Speed vs Safety trade-off.
        time.sleep(random.uniform(0.5, 1.5))
        
        # Simple heuristic: Get all <p> tags
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        text_content = " ".join([p.text for p in paragraphs if len(p.text) > 50])
        
        if len(text_content) < 200:
            return None # Failed or anti-bot challenge
            
        return text_content
    except Exception as e:
        print(f"Scrape Error or Timeout: {e}", flush=True)
        return None

def worker_main():
    print(f"--- STARTING CLOUD WORKER ---", flush=True)
    print(f"Target: {len(TOP_150_STOCKS)} Stocks", flush=True)
    
    db = NewsDatabase()
    driver = setup_driver()
    
    total_processed = 0
    total_articles = 0
    
    for ticker in TOP_150_STOCKS:
        # Using Google News RSS (Snippet) as Discovery Source
        rss_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:1d&hl=en-US&gl=US&ceid=US:en"
        
        # We use a simple request to get the RSS first (fast)
        # Then use Selenium for the DEEP links
        import feedparser
        feed = feedparser.parse(rss_url)
        
        print(f"[{ticker}] Found {len(feed.entries)} entries.", flush=True)
        
        # Custom Logic: 5 Full Text + 15 Snippets = 20 Total
        entries = feed.entries[:20]
        
        for i, entry in enumerate(entries):
            link = entry.link
            title = entry.title
            
            # Logic: Top 5 get Full Text Scrape (High resource usage)
            # The rest (6-20) get Snippet only (Zero resource usage)
            should_scrape_full = (i < 5)
            
            full_text = None
            if should_scrape_full:
                full_text = scrape_full_text(driver, link)
            
            # Use Full Text if available, else Snippet
            if full_text:
                text_to_analyze = full_text
                source_type = "full_text"
            else:
                text_to_analyze = title + ". " + (entry.summary if hasattr(entry, 'summary') else "")
                source_type = "snippet"
            
            # --- AI ANALYSIS ---
            sentiment = analyze_sentiment(text_to_analyze)
            
            # --- SAVE TO DB ---
            article_data = {
                "link": link,
                "title": title,
                "published": time.strftime('%Y-%m-%d', entry.published_parsed) if hasattr(entry, 'published_parsed') else "",
                "publisher": entry.source.title if hasattr(entry, 'source') else "Google News",
                "text": full_text, # Can be None
                "snippet": entry.summary[:500] if hasattr(entry, 'summary') else "",
                "sentiment": sentiment,
                "debug": {
                    "source": source_type,
                    "worker_version": "1.1 (Hybrid 5/15)"
                }
            }
            
            db.upsert_article(ticker, None, article_data)
            total_articles += 1
            
        total_processed += 1
        # Sleep to avoid rate limits
        time.sleep(1.0)
        
    driver.quit()
    print(f"--- WORKER COMPLETE ---")
    print(f"Stocks Scanned: {total_processed}")
    print(f"Articles Saved: {total_articles}")

if __name__ == "__main__":
    worker_main()
