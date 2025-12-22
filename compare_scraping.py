import trafilatura
from brain.sentiment.scraper import fetch_url as current_fetch
import requests
from bs4 import BeautifulSoup

# A mix of likely-blocked and likely-open URLs
urls = {
    "Yahoo Finance": "https://finance.yahoo.com/news/nvidia-stock-price-prediction-2025-130018544.html",
    "CNBC (Usually Tough)": "https://www.cnbc.com/2025/12/20/nvidia-stock-buy-sell-hold-analyst-ratings.html",
    "Generic Tech Blog (Easier)": "https://techcrunch.com/2024/12/15/ai-startups-funding-trends/" 
}

# Note: Using random legitimate-looking URLs for demonstration. 
# If these 404, we will use the scraper's redirect logic on a google news link.

google_news_link = "https://news.google.com/rss/articles/CBMidkFVX3lxTFAzUzlnbFQtNGZpd0RVd3dDYk1OX25JdFkzNU9adkIxOWFPVlRRZ3RoNHNrM2VwZEFqMXo3ZWlYelVsZk9IdDRWRHA5LUZkTF8wclVTRHZLNDgwQWtSQkVFc2hCc29SWmpNUmVXOGxoWGNKRjgxa0E?oc=5"

print("--- DEMONSTRATION: Snippet vs Full Text ---\n")

def get_snippet(url):
    # current method (BS4 paragraphs)
    text, status, t = current_fetch(url, timeout=5.0)
    if text:
        return text[:300] + "..."
    return "FAILED to fetch."

def get_trafilatura(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return text[:500] + "\n...[REST OF FULL TEXT]..."
    except:
        pass
    return "FAILED to extract."

# Test on Google News Link (Redirect handling needed)
print(f"Target: Google News Link (Redirects to Yahoo/Other)")
print(f"URL: {google_news_link}\n")

print("[Current Method (Extended Snippet)]:")
print(get_snippet(google_news_link))
print("-" * 40)

print("[Trafilatura (Potential Full Text)]:")
# Trafilatura handles redirects well usually
print(get_trafilatura(google_news_link))
print("=" * 60)
