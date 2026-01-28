import sys
import os
import re
import feedparser

# Fetch live data
rss_url = "https://news.google.com/rss/search?q=MSFT+stock&hl=en-US&gl=US&ceid=US:en"
feed = feedparser.parse(rss_url)

if feed.entries:
    entry = feed.entries[0]
    
    print("\n--- COMPONENTS ---")
    print(f"1. TITLE: \n{entry.title}\n")
    
    raw_desc = entry.description if hasattr(entry, 'description') else ""
    # clean it like we do in the app
    clean_desc = re.sub(r'<[^>]+>', '', raw_desc)
    
    print(f"2. DESCRIPTION (Cleaned): \n{clean_desc}\n")
    
    print("--- FINAL SNIPPET (What the AI reads) ---")
    print(f"{entry.title}. {clean_desc}")
else:
    print("No entries found.")
