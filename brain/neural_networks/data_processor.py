import pandas as pd
import numpy as np
import os
import requests
import pickle
from sklearn.preprocessing import StandardScaler

class DataProcessor:
    def __init__(self, sequence_length=60, scaler_path="brain/saved_models/scaler.pkl"):
        self.sequence_length = sequence_length
        self.scaler_path = scaler_path
        self.scaler = StandardScaler()
        
    def save_scaler(self):
        os.makedirs(os.path.dirname(self.scaler_path), exist_ok=True)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
            
    def load_scaler(self):
        if os.path.exists(self.scaler_path):
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            return True
        return False
        
    def fetch_stock_history(self, ticker):
        try:
            api_key = os.getenv("TWELVE_DATA_KEY")
            url = "https://api.twelvedata.com/time_series"
            params = {"symbol": ticker, "interval": "1day", "outputsize": "5000", "apikey": api_key}
            response = requests.get(url, params=params)
            data = response.json()
            if "values" not in data: return None
            df = pd.DataFrame(data['values'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'})
            return df.iloc[::-1].reset_index(drop=True)
        except: return None

    def add_technical_indicators(self, df):
        df = df.copy()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        ma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = (ma20 + (std20 * 2)) / df['Close']
        df['BB_Lower'] = (ma20 - (std20 * 2)) / df['Close']
        return df.dropna()

    def create_sequences(self, data, targets):
        xs, ys = [], []
        for i in range(self.sequence_length, len(data)):
            xs.append(data[i-self.sequence_length:i])
            ys.append(targets[i])
        return np.array(xs), np.array(ys)

    def prepare_ticker_data(self, ticker):
        """
        Processes a single ticker with strict time-series splitting and no leakage.
        """
        df = self.fetch_stock_history(ticker)
        if df is None: return None
        
        df = self.add_technical_indicators(df)
        
        # 1. GENERATE LABELS ON RAW DATA (Leakage Fix #3)
        prediction_horizon = 5
        # Target: Is the price 5 days from now higher than today?
        df['Target_Return'] = df['Close'].shift(-prediction_horizon) / df['Close'] - 1
        df['Target'] = (df['Target_Return'] > 0).astype(int)
        
        # 2. FEATURE ENGINEERING (Stationarity)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = df[col].pct_change()
        
        # Drop rows with NaNs from targets/returns and technical indicators
        # Also handle potential infinity from pct_change(0)
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 'Volatility', 'BB_Upper', 'BB_Lower']
        # Sentiment/News placeholders for consistency with model input size (13)
        df['Sentiment'] = 0.0
        df['NewsVol'] = 0.0
        feature_cols += ['Sentiment', 'NewsVol']
        
        # 3. TIME-BASED SPLIT (Leakage Fix #1)
        split_idx = int(0.8 * len(df))
        
        # Add a GAP to prevent overlap (Leakage Fix #4)
        # We need a gap so the validation set doesn't use any price data seen in training windows
        gap = self.sequence_length + prediction_horizon
        train_df = df.iloc[:split_idx - gap]
        val_df = df.iloc[split_idx:]
        
        if len(train_df) < self.sequence_length or len(val_df) < self.sequence_length:
            return None

        # 4. SCALING: Fit on Train ONLY, transform both (Leakage Fix #2)
        train_features = train_df[feature_cols].values
        val_features = val_df[feature_cols].values
        
        # Fit scaler on training portion of this ticker
        ticker_scaler = StandardScaler()
        train_scaled = ticker_scaler.fit_transform(train_features)
        val_scaled = ticker_scaler.transform(val_features)
        
        # We'll save the "global" version later, but for multi-ticker training, 
        # we scale each ticker by its own historical distribution.
        
        # 5. Create Sequences
        x_train, y_train = self.create_sequences(train_scaled, train_df['Target'].values)
        x_val, y_val = self.create_sequences(val_scaled, val_df['Target'].values)
        
        return x_train, y_train, x_val, y_val

    def prepare_inference_data(self, graph_data):
        if not graph_data or len(graph_data) < self.sequence_length + 25: return None 
        df = pd.DataFrame(graph_data).rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = self.add_technical_indicators(df)
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = df[col].pct_change()
            
        df = df.dropna().replace([np.inf, -np.inf], 0)
        feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 'Sentiment', 'NewsVol', 'Volatility', 'BB_Upper', 'BB_Lower']
        
        # For inference, use the saved global scaler
        if not self.load_scaler(): return None
        scaled_data = self.scaler.transform(df[feature_cols].values)
        return np.array([scaled_data[-self.sequence_length:]]) if len(scaled_data) >= self.sequence_length else None