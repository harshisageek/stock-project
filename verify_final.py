
import json

try:
    with open("verification_output_final.json", "r") as f:
        data = json.load(f)
        
    news = data.get("news", [])
    print(f"Total News returned: {len(news)}")
    
    neutrals = [n for n in news if abs(n['sentiment']) < 0.01]
    
    print("\n--- Sentiment Scores (First 5) ---")
    for n in news[:5]:
        print(f"{n['sentiment']}: {n['title'][:50]}...")
        
    if len(news) >= 20:
        print("\n[PASS] Article count is >= 20.")
    else:
        print(f"\n[FAIL] Article count {len(news)} < 20.")
        
    if len(neutrals) == 0:
         print("[PASS] No zero-score articles found.")
    else:
         print(f"[FAIL] Found {len(neutrals)} zero-score articles.")
         
except Exception as e:
    print(f"Verification Error: {e}")
