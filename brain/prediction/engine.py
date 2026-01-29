import os
import torch
import numpy as np
import logging
import joblib
import pandas as pd
from typing import List, Tuple
from brain.core.config import BrainConfig
from brain.core.types import StockDataPoint
from brain.prediction.lstm import StockLSTM

logger = logging.getLogger(__name__)

class PredictionEngine:
    """
    Manages the PyTorch LSTM model for price direction prediction.
    Fixes feature ordering bugs from legacy implementation.
    """
    def __init__(self):
        self.config = BrainConfig.get_instance()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.scaler = None
        self._loaded = False
        
    def _load_resources(self):
        if self._loaded:
            return

        # Load Scaler
        if os.path.exists(self.config.SCALER_PATH):
            try:
                self.scaler = joblib.load(self.config.SCALER_PATH)
            except Exception as e:
                logger.error(f"Scaler load failed: {e}")
                return
        else:
            logger.warning("Scaler not found. Prediction disabled.")
            return

        # Load Model
        try:
            self.model = StockLSTM(input_size=13) # Architecture fixed
            if os.path.exists(self.config.MODEL_PATH):
                state = torch.load(self.config.MODEL_PATH, map_location=self.device)
                self.model.load_state_dict(state)
                self.model.to(self.device)
                self.model.eval()
                self._loaded = True
                logger.info("Neural Model Loaded Successfully.")
            else:
                logger.warning("Model weights not found.")
        except Exception as e:
            logger.error(f"Model load failed: {e}")

    def prepare_data(self, data: List[StockDataPoint], sequence_length=60):
        """
        Prepares data for inference (Feature Engineering + Scaling).
        """
        if not data or len(data) < sequence_length + 30: # Need extra buffer for indicators
            return None
            
        # 1. Convert to DataFrame
        # Map Pydantic fields to expected internal names
        records = [
            {
                'Open': d.open, 
                'High': d.high, 
                'Low': d.low, 
                'Close': d.close, 
                'Volume': d.volume,
                'datetime': d.datetime
            } 
            for d in data
        ]
        df = pd.DataFrame(records)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)
        
        # 2. Add Technical Indicators (Manual Implementation to match training logic)
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
        
        # 3. Pct Change for OHLCV
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = df[col].pct_change()
            
        # 4. Add Missing Features (Sentiment/NewsVol)
        # Note: In inference, we might have global sentiment, but the model expects per-day.
        # Ideally we map historical sentiment, but for now we default to 0.0 like training.
        df['Sentiment'] = 0.0 
        df['NewsVol'] = 0.0
        
        # 5. Clean
        df = df.dropna().replace([np.inf, -np.inf], 0)
        
        if len(df) < sequence_length:
            return None
            
        # 6. Select Features in CORRECT ORDER (Matching prepare_ticker_data)
        feature_cols = [
            'Open', 'High', 'Low', 'Close', 'Volume', 
            'RSI', 'MACD', 'MACD_Signal', 'Volatility', 
            'BB_Upper', 'BB_Lower', 'Sentiment', 'NewsVol'
        ]
        
        # 7. Scale
        try:
            scaled_data = self.scaler.transform(df[feature_cols].values)
            # Return last sequence
            return np.array([scaled_data[-sequence_length:]])
        except Exception as e:
            logger.error(f"Scaling error: {e}")
            return None

    def predict(self, data: List[StockDataPoint]) -> Tuple[str, float]:
        self._load_resources()
        
        if not self._loaded or not self.scaler:
            return "Neutral (Model Off)", 0.0
            
        try:
            input_tensor_np = self.prepare_data(data)
            
            if input_tensor_np is None:
                return "Neutral (Need More Data)", 0.0
                
            input_tensor = torch.FloatTensor(input_tensor_np).to(self.device)
            
            with torch.no_grad():
                logits = self.model(input_tensor)
                prediction = torch.sigmoid(logits).item()
                
            signal = "Bullish" if prediction > 0.50 else "Bearish"
            return signal, prediction
            
        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return "Neutral (Error)", 0.0