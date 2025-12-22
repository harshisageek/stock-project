from brain.sentiment.scraper import fetch_url
from brain.sentiment.analyzer import analyze_sentiment

# Link from the JSON response in Step 311 (one that returned success but snippet fallback)
# "Tesla Stock (TSLA) in December 2025: ..."
test_link = "https://news.google.com/rss/articles/CBMipAFBVV95cUxQS2NZTXpEcFpCLWJ2VHl4TWFvNW5PSkU1Q0xKTmxNX1V0VEJWTjFVanVGd0dmMUlMOWdDZ0xnMkdjdkZHbFY5cTl2SG5qRmxPNWNuNldMMWg0SDFVV3FMUGMzUGNJT0R6TTRjOFZ2RnRtaHl5QkZXbzBXRzVJV1VOOXlNcWxqS3MwbmxmTG14X0xLTHpNWS1ONHF5WFJKb0FMMTJpNQ?oc=5"

print(f"--- Testing Scraper on: {test_link} ---")
text, status, time_taken = fetch_url(test_link, timeout=5.0)

print(f"Status: {status}")
print(f"Time: {time_taken}")
print(f"Text Length: {len(text) if text else 0}")
print(f"Text Snippet: {text[:200] if text else 'None'}")

if text:
    print(f"\n--- Testing FinBERT on Full Text ---")
    score = analyze_sentiment(text)
    print(f"Sentiment Score: {score}")
else:
    print("\nNo text to analyze.")

print(f"\n--- Testing FinBERT on Dummy Headline ---")
dummy = "Tesla stock soars as earnings beat expectations."
score = analyze_sentiment(dummy)
print(f"Dummy text: {dummy}")
print(f"Score: {score}")
