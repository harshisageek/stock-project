
import requests
from bs4 import BeautifulSoup

def scrape_stock_analysis(endpoint):
    base_url = "https://stockanalysis.com/markets"
    url = f"{base_url}/{endpoint}/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Scraping {url}...")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        
        if res.status_code != 200:
            return []
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Find the main table
        # StockAnalysis usually puts data in a standard <table>
        table = soup.find('table')
        if not table:
            print("No table found!")
            return []
            
        rows = table.find_all('tr')[1:6] # Skip header, get top 5
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            # Structure changes sometimes, but usually:
            # Symbol | Name | Price | Change | % Change | Volume
            
            symbol = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            price = cols[2].get_text(strip=True)
            change_pct = cols[3].get_text(strip=True) # Check if this is change or %
            
            # Check if 4th col is % or if 5th is
            # On StockAnalysis: Sym, Name, Price, Change, %Change, Vol, MktCap
            if '%' not in change_pct and len(cols) > 4:
                change_pct = cols[4].get_text(strip=True)
                
            # Volume usually last or near end
            volume = cols[-2].get_text(strip=True)
            
            data.append({
                "symbol": symbol,
                "name": name,
                "price": f"${price}",
                "change": change_pct.replace('%', ''),
                "volume": volume
            })
            
        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Gainers:")
    print(scrape_stock_analysis("gainers"))
    print("\nLosers:")
    print(scrape_stock_analysis("losers"))
    print("\nActive:")
    print(scrape_stock_analysis("active"))
