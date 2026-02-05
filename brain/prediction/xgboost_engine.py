import pandas as pd
import numpy as np
import xgboost as xgb
import os
import logging
from typing import List, Tuple
from brain.core.config import BrainConfig
from brain.core.types import StockDataPoint
from brain.core.indicators import add_technical_indicators
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    """
    The 'Quant Analyst'.
    Uses a PRE-TRAINED XGBoost model to predict probability of significant price increase.
    INFERENCE ONLY.
    """
    def __init__(self):
        self.config = BrainConfig.get_instance()
        self.model = None
        self._is_ready = False
        
        # Exact feature order for Training and Inference consistency
        # Updated to Stationary Features
        self.FEATURE_COLS = [
            'Log_Ret', 'RSI', 'MACD', 'MACD_Signal', 
            'BB_Pct', 'Vol_Ratio', 'ROC', 
            'SMA_Ratio',
            'Sentiment', 'NewsVol'
        ]
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        self.model_path = os.path.join(base_dir, "saved_models", "xgboost_model.json")
        
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                self._is_ready = True
                logger.info(f"XGBoost Model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load XGBoost model: {e}")
        else:
            logger.warning(f"XGBoost model file not found at {self.model_path}. Predictor disabled.")

    def predict_probability(self, data: List[StockDataPoint]) -> Tuple[str, float]:
        """
        Returns (Signal, Probability).
        Signal: "Bullish" | "Bearish" | "Neutral"
        Probability: 0.0 to 1.0 (Probability of UP move)
        """
        if not self._is_ready or not self.model:
            return "Neutral (Model Missing)", 0.5
            
        if not data or len(data) < 50:
            return "Neutral (Low Data)", 0.5

        # 1. Convert to DataFrame
        records = [{'close': d.close, 'open': d.open, 'high': d.high, 'low': d.low, 'volume': d.volume} for d in data]
        df = pd.DataFrame(records)
        
        # 2. Feature Engineering (Centralized)
        df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = add_technical_indicators(df)
        
        # Fill missing features
        df['Sentiment'] = 0.0
        df['NewsVol'] = 0.0
        
        # Drop NaNs
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        if df.empty:
            return "Neutral", 0.5
            
        # 3. Dynamic Scaling (CRITICAL)
        try:
            scaler = StandardScaler()
            # Fit on the entire window (dynamic scaling)
            features = df[self.FEATURE_COLS].values
            scaled_features = scaler.fit_transform(features)
            
            # Select the LAST row (current state)
            last_row = scaled_features[-1].reshape(1, -1)
            
            # 4. Predict
            # predict_proba returns [[prob_0, prob_1]]
            probs = self.model.predict_proba(last_row)[0]
            prob_up = float(probs[1])
            
            # 5. Threshold Logic (0.6 / 0.4)
            if prob_up > 0.6:
                signal = "Bullish"
            elif prob_up < 0.4:
                signal = "Bearish"
            else:
                signal = "Neutral"
                
            return signal, round(prob_up, 4)
            
        except Exception as e:
            logger.error(f"XGB Inference Error: {e}")
            return "Neutral (Error)", 0.5
