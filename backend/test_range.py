
import requests
try:
    r = requests.get('http://127.0.0.1:5000/api/analyze?ticker=AAPL&range=1M')
    data = r.json()
    count = len(data.get("graph_data", []))
    print(f"Graph Data Points: {count}")
    print(f"Cached: {data.get('cached')}")
except Exception as e:
    print(f"Error: {e}")
