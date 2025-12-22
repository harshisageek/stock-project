import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv

# Load env vars for API key
# Load env vars for API key
load_dotenv()

class DataProcessor:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def fetch_stock_history(self, ticker, period="2y"):
        """
        Fetches historical OHLCV data using Twelve Data API.
        """
        try:
            import requests
            import os
            
            api_key = os.getenv("TWELVE_DATA_KEY")
            if not api_key:
                print("Error: TWELVE_DATA_KEY not found.")
                return None

            # Twelve Data API
            # outputsize=5000 covers >10 years of daily data
            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": ticker,
                "interval": "1day",
                "outputsize": "5000", 
                "apikey": api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "values" not in data:
                print(f"Twelve Data Error: {data.get('message', 'Unknown error')}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(data['values'])
            
            # Twelve Data returns strings, convert to float
            cols = ['open', 'high', 'low', 'close', 'volume']
            for col in cols:
                df[col] = df[col].astype(float)
                
            # Rename columns to Title Case to match previous logic (Open, High, Low...)
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'
            })
            
            # Twelve Data returns newest first. We need oldest first.
            df = df.iloc[::-1].reset_index(drop=True)
            
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def add_technical_indicators(self, df):
        """
        Adds RSI and MACD using the existing QuantEngine logic.
        """
        # We need to adapt QuantEngine to work on DataFrame or re-implement heavily optimized vector logic here.
        # For training speed, vectorization (pandas) is better than the loop in QuantEngine.
        
        # 1. RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        # Signal line not strictly needed for raw input, but helps context
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df.dropna()

    def merge_sentiment(self, price_df, sentiment_data=None):
        """
        Merges Price DataFrame with Sentiment Data.
        If sentiment_data is None (Training on old data), we impute Neutral (0.0).
        """
        # Feature Engineering: Add 'Sentiment' and 'NewsVol' columns
        # In a real scenario, this would merge on Date.
        # For MVP Training (Cold Start), we will assume 'Neutral' sentiment for historical data
        # unless provided.
        
        if sentiment_data is None:
            price_df['Sentiment'] = 0.0 # Neutral
            price_df['NewsVol'] = 0.0 # No News
        else:
            # TODO: Implement merge logic when we have DB history
            price_df['Sentiment'] = 0.0 
            price_df['NewsVol'] = 0.0
            
        return price_df

    def prepare_data(self, ticker):
        """
        Full pipeline: Fetch -> Indicator -> Normalize -> Sequence
        """
        # 1. Fetch
        df = self.fetch_stock_history(ticker)
        if df is None:
            return None, None
            
        # 2. Indicators
        df = self.add_technical_indicators(df)
        
        # 3. Sentiment (Placeholder for now)
        df = self.merge_sentiment(df)
        
        # 4. Normalize
        # Features: Open, High, Low, Close, Volume, RSI, MACD, MACD_Signal, Sentiment, NewsVol
        feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 'Sentiment', 'NewsVol']
        data = df[feature_cols].values
        
        scaled_data = self.scaler.fit_transform(data)
        
        x_train = []
        y_train = []
        
        # Create Sequences
        # We want to predict if Close price tomorrow > Close price today
        
        for i in range(self.sequence_length, len(scaled_data) - 1):
            x_train.append(scaled_data[i-self.sequence_length:i])
            
            # Target generation:
            # 1 = Price UP tomorrow
            # 0 = Price DOWN/FLAT tomorrow
            
            # Note: We need unscaled Close price to determine direction accurately, 
            # effectively checking change in normalized Close is same as real Close.
            
            price_today = scaled_data[i][3] # Close is index 3
            price_tomorrow = scaled_data[i+1][3]
            
            target = 1 if price_tomorrow > price_today else 0
            y_train.append(target)
            
        return np.array(x_train), np.array(y_train)
