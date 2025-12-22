from brain.sentiment.scraper import fetch_url
import trafilatura
import requests
from bs4 import BeautifulSoup

# A Google News link that redirects to something (hopefully)
target_url = "https://news.google.com/rss/articles/CBMidkFVX3lxTFAzUzlnbFQtNGZpd0RVd3dDYk1OX25JdFkzNU9adkIxOWFPVlRRZ3RoNHNrM2VwZEFqMXo3ZWlYelVsZk9IdDRWRHA5LUZkTF8wclVTRHZLNDgwQWtSQkVFc2hCc29SWmpNUmVXOGxoWGNKRjgxa0E?oc=5"

print(f"Original: {target_url}")

# 1. Resolve Redirect manually (simplified version of scraper.py logic)
def resolve_google_redirect(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Referer": "https://news.google.com/"
        }
        response = requests.get(url, headers=headers, timeout=5.0)
        
        # Check if we are still on Google
        if "news.google.com" in response.url or "consent.google.com" in response.url:
             soup = BeautifulSoup(response.content, 'lxml')
             links = soup.find_all('a', href=True)
             for link in links:
                 href = link['href']
                 if href.startswith("http") and "google.com" not in href:
                     return href
        return response.url # Maybe it resolved automatically?
    except Exception as e:
        print(f"Resolve Error: {e}")
        return None

real_url = resolve_google_redirect(target_url)
print(f"Resolved URL: {real_url}")

if real_url and "google.com" not in real_url:
    print("Attempting Trafilatura extraction on Resolved URL...")
    downloaded = trafilatura.fetch_url(real_url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        if text:
            print("\n[SUCCESS - FULL TEXT EXTRACTED]")
            print(text[:500] + "...")
        else:
            print("[FAILED - Trafilatura could not extract text]")
            print(f"Downloaded content length: {len(downloaded)}")
    else:
        print("[FAILED - Trafilatura could not fetch]")
else:
    print("[Skipping Trafilatura - Could not resolve to non-google link]")
