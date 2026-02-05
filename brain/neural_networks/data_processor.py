import pandas as pd
import numpy as np
import os
import requests
import pickle
import logging
from sklearn.preprocessing import StandardScaler
from brain.core.indicators import add_technical_indicators

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, sequence_length=60, scaler_path="brain/saved_models/scaler.pkl"):
        self.sequence_length = sequence_length
        self.scaler_path = scaler_path
        self.scaler = StandardScaler()
        self.target_mean = 0.0
        self.target_std = 1.0
        
        self.FEATURE_COLS = [
            'Log_Ret', 'RSI', 'MACD', 'MACD_Signal', 
            'BB_Pct', 'Vol_Ratio', 'ROC', 
            'SMA_Ratio', 'ATR_Pct', 'CCI', 
            'Ret_1d', 'Ret_3d', 'Ret_5d', 'Ret_10d', 'Ret_20d',
            'Sentiment', 'NewsVol'
        ]
        
    def save_scaler(self):
        os.makedirs(os.path.dirname(self.scaler_path), exist_ok=True)
        data = {
            'scaler': self.scaler,
            'mean': self.target_mean,
            'std': self.target_std
        }
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Scaler & Target Stats saved to {self.scaler_path}")
            
    def load_scaler(self):
        if os.path.exists(self.scaler_path):
            with open(self.scaler_path, 'rb') as f:
                data = pickle.load(f)
                # Handle legacy format (just scaler) vs new dict format
                if isinstance(data, dict):
                    self.scaler = data['scaler']
                    self.target_mean = data.get('mean', 0.0)
                    self.target_std = data.get('std', 1.0)
                else:
                    self.scaler = data
            return True
        return False
        
    def fetch_stock_history(self, ticker):
        try:
            api_key = os.getenv("TWELVE_DATA_KEY")
            url = "https://api.twelvedata.com/time_series"
            params = {"symbol": ticker, "interval": "1day", "outputsize": "5000", "apikey": api_key}
            response = requests.get(url, params=params)
            data = response.json()
            
            if "values" not in data:
                print(f"[API Error] {ticker}: {data.get('message', 'Unknown Error')}")
                return None
                
            df = pd.DataFrame(data['values'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'})
            return df.iloc[::-1].reset_index(drop=True)
        except Exception as e:
            print(f"[Network Error] {e}")
            return None

    def create_sequences(self, data, targets):
        xs, ys = [], []
        for i in range(self.sequence_length, len(data)):
            xs.append(data[i-self.sequence_length:i])
            ys.append(targets[i])
        return np.array(xs), np.array(ys)

    def prepare_ticker_data(self, ticker):
        df = self.fetch_stock_history(ticker)
        if df is None: return None
        
        # 1. Feature Engineering
        df = add_technical_indicators(df)
        
        # 2. Target (Classification): 3-Class System
        horizon = 5
        future_ret = (df['Close'].shift(-horizon) / df['Close'] - 1) * 100
        
        # Thresholds: +/- 1.5%
        # 0 = Sell, 1 = Hold, 2 = Buy
        conditions = [
            (future_ret < -1.5),
            (future_ret > 1.5)
        ]
        choices = [0, 2] # Sell, Buy
        df['Target_Class'] = np.select(conditions, choices, default=1) # Default Hold
        
        # Fill features
        df['Sentiment'] = 0.0
        df['NewsVol'] = 0.0
        
        # Clean
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Split
        split_idx = int(0.8 * len(df))
        gap = self.sequence_length + horizon
        train_df = df.iloc[:split_idx - gap]
        val_df = df.iloc[split_idx:]
        
        if len(train_df) < self.sequence_length: return None

        # Scaling
        train_features = train_df[self.FEATURE_COLS].values
        val_features = val_df[self.FEATURE_COLS].values
        
        self.scaler.fit(train_features)
        train_scaled = self.scaler.transform(train_features)
        val_scaled = self.scaler.transform(val_features)
        
        # Sequences (Return Class Targets)
        x_tr, y_tr = self.create_sequences(train_scaled, train_df['Target_Class'].values)
        x_val, y_val = self.create_sequences(val_scaled, val_df['Target_Class'].values)
        
        return x_tr, y_tr, x_val, y_val

    def prepare_inference_data(self, graph_data):
        if not graph_data or len(graph_data) < self.sequence_length + 30: return None 
        
        df = pd.DataFrame(graph_data).rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = add_technical_indicators(df)
        
        df['Sentiment'] = 0.0
        df['NewsVol'] = 0.0
            
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        try:
            dynamic_scaler = StandardScaler()
            features = df[self.FEATURE_COLS].values
            scaled_data = dynamic_scaler.fit_transform(features)
            if len(scaled_data) < self.sequence_length: return None
            return np.array([scaled_data[-self.sequence_length:]])
        except Exception as e:
            logger.error(f"Inference prep error: {e}")
            return None