import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

# List of trusted financial domains
TRUSTED_SOURCES = [
    "bloomberg.com", "reuters.com", "cnbc.com", "wsj.com", "ft.com", 
    "finance.yahoo.com", "marketwatch.com", "seekingalpha.com", "investing.com"
]

def fetch_url(url, timeout=4.0):
    """
    Fetch a single URL with a strict timeout.
    Attempts to follow Google News redirects.
    Returns (text_content, status, time_taken)
    """
    start_time = time.time()
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://news.google.com/"
        }
        
        # First request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Check if we are still on Google News (Redirect Page)
        # Google Redirects often have a link: <a href="..." jsname="...">Open</a> or similar
        # Or standard <a href> in the body
        if "news.google.com" in response.url or "consent.google.com" in response.url:
             # Try to find the real link
             # Strategy: Find all links, pick the one that is NOT google.com
             links = soup.find_all('a', href=True)
             for link in links:
                 href = link['href']
                 if href.startswith("http") and "google.com" not in href:
                     # Follow this link
                     return fetch_url(href, timeout=timeout)
        
        # If we are valid content
        paragraphs = soup.find_all('p')
        # Get first 10 paragraphs or 5000 chars
        text = " ".join([p.get_text() for p in paragraphs[:15]])
        text = text[:5000].strip()
        
        if len(text) < 100:
             # Too short, maybe failed to parse or blocked
             return None, "empty_content", time.time() - start_time
        
        elapsed = time.time() - start_time
        return text, "success", elapsed
        
    except requests.exceptions.Timeout:
        return None, "timeout", time.time() - start_time
    except Exception as e:
        return None, "error", time.time() - start_time

def scrape_articles_parallel(articles, timeout=4.0):
    """
    Scrape multiple articles in parallel.
    
    Args:
        articles: List of dicts with 'link' key.
        timeout: Max seconds to wait for each request.
        
    Returns:
        List of results matched to input articles.
    """
    results = [None] * len(articles)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {
            executor.submit(fetch_url, article['link'], timeout): i 
            for i, article in enumerate(articles)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            try:
                text, status, time_taken = future.result()
                results[i] = {
                    "text": text,
                    "status": status,
                    "time_taken": round(time_taken, 2)
                }
            except Exception as e:
                results[i] = {
                    "text": None,
                    "status": "error", 
                    "time_taken": 0.0
                }
                
    return results

def calculate_source_weight(url):
    """
    Get weight (0.5 to 1.5) based on domain authority.
    """
    for domain in TRUSTED_SOURCES:
        if domain in url:
            return 1.5 # High authority
    return 1.0 # Standard authority
