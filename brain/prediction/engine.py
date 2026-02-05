import os
import torch
import numpy as np
import logging
import pickle
import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import StandardScaler 
from brain.core.config import BrainConfig
from brain.core.types import StockDataPoint
from brain.neural_networks.model import StockLSTM
from brain.core.indicators import add_technical_indicators

logger = logging.getLogger(__name__)

class PredictionEngine:
    """
    Manages the PyTorch LSTM model for price direction prediction.
    """
    def __init__(self):
        self.config = BrainConfig.get_instance()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.scaler = None
        self.target_mean = 0.0
        self.target_std = 1.0
        self._loaded = False
        self.FEATURE_COLS = [
            'Log_Ret', 'RSI', 'MACD', 'MACD_Signal', 
            'BB_Pct', 'Vol_Ratio', 'ROC', 
            'SMA_Ratio', 'ATR_Pct', 'CCI', 
            'Ret_1d', 'Ret_3d', 'Ret_5d', 'Ret_10d', 'Ret_20d',
            'Sentiment', 'NewsVol'
        ]
        
    def _load_resources(self):
        if self._loaded:
            return

        try:
            # Load Model
            self.model = StockLSTM(input_size=17) 
            if os.path.exists(self.config.MODEL_PATH):
                state = torch.load(self.config.MODEL_PATH, map_location=self.device)
                self.model.load_state_dict(state)
                self.model.to(self.device)
                self.model.eval()
            else:
                logger.warning("Model weights not found.")
                return

            # Load Scaler & Target Stats
            scaler_path = "brain/saved_models/scaler.pkl"
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.scaler = data['scaler']
                        self.target_mean = data.get('mean', 0.0)
                        self.target_std = data.get('std', 1.0)
                    else:
                        self.scaler = data
                        
                logger.info(f"Neural Resources Loaded. Target Mean: {self.target_mean:.4f}, Std: {self.target_std:.4f}")
                self._loaded = True
            else:
                logger.warning("Scaler not found. Predictions will be inaccurate.")

        except Exception as e:
            logger.error(f"Resource load failed: {e}")

    def prepare_data(self, data: List[StockDataPoint], sequence_length=60):
        if not data or len(data) < sequence_length + 30: 
            return None
            
        records = [
            {'Open': d.open, 'High': d.high, 'Low': d.low, 'Close': d.close, 'Volume': d.volume, 'datetime': d.datetime} 
            for d in data
        ]
        df = pd.DataFrame(records)
        
        df = add_technical_indicators(df)
        df['Sentiment'] = 0.0 
        df['NewsVol'] = 0.0
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        try:
            # Use the PRE-TRAINED scaler, do not fit a new one!
            if self.scaler is None:
                logger.error("Scaler not loaded.")
                return None
                
            features = df[self.FEATURE_COLS].values
            scaled_data = self.scaler.transform(features)
            
            if len(scaled_data) < sequence_length: return None
            return np.array([scaled_data[-sequence_length:]])
        except Exception as e:
            logger.error(f"Scaling error: {e}")
            return None

    def predict(self, data: List[StockDataPoint]) -> Tuple[str, float]:
        """
        Returns:
            signal (str): "Bullish", "Bearish", or "Neutral"
            confidence (float): Probability (0.0 to 1.0)
        """
        self._load_resources()
        
        if not self._loaded:
            return "Neutral (Model Off)", 0.0
            
        try:
            input_tensor_np = self.prepare_data(data)
            
            if input_tensor_np is None:
                return "Neutral (Need More Data)", 0.0
                
            input_tensor = torch.FloatTensor(input_tensor_np).to(self.device)
            
            with torch.no_grad():
                # CLASSIFICATION OUTPUT (Logits for 3 classes)
                logits = self.model(input_tensor)
                probs = torch.softmax(logits, dim=1) # [Sell, Hold, Buy]
                
                # Get the class with highest probability
                confidence, predicted_class = torch.max(probs, 1)
                class_idx = predicted_class.item()
                conf_val = confidence.item()
                
            # Map Class Index to Signal
            # 0 = Sell, 1 = Hold, 2 = Buy
            if class_idx == 2:
                signal = "Bullish"
            elif class_idx == 0:
                signal = "Bearish"
            else:
                signal = "Neutral"
            
            return signal, conf_val
            
        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return "Neutral (Error)", 0.0
