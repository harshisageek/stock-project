
import requests

def test_fmp():
    api_key = "hadAI83yZSwLLiiZ6QmquxaWAW1BWhHf"
    base_url = "https://financialmodelingprep.com/api/v3/stock_market"
    endpoints = ["gainers", "losers", "actives"]
    
    for ep in endpoints:
        url = f"{base_url}/{ep}?apikey={api_key}"
        print(f"Fetching {ep} from: {url}")
        
        try:
            res = requests.get(url, timeout=10)
            print(f"Status Code: {res.status_code}")
            
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    print(f"Success! Received {len(data)} items.")
                    if len(data) > 0:
                        print("Sample item:", data[0])
                else:
                    print("Response is not a list:", data)
            else:
                print("Error Response:", res.text)
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_fmp()
