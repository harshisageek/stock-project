import pandas as pd
import numpy as np
import xgboost as xgb
import os
import logging
from typing import List, Tuple
from brain.core.config import BrainConfig
from brain.core.types import StockDataPoint

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    """
    The 'Quant Analyst'.
    Uses a PRE-TRAINED XGBoost model to predict probability of significant price increase.
    INFERENCE ONLY. No on-the-fly training.
    """
    def __init__(self):
        self.config = BrainConfig.get_instance()
        self.model = None
        self._is_ready = False
        self.model_path = "brain/saved_models/xgboost_model.json"
        
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

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates features: RSI, MACD, BB, ROC.
        MUST match training script logic exactly.
        """
        if len(df) < 30: return df
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['upper_bb'] = df['ma20'] + (df['std'] * 2)
        df['lower_bb'] = df['ma20'] - (df['std'] * 2)
        
        # ROC (Rate of Change)
        df['roc'] = df['close'].pct_change(periods=10) * 100
        
        return df.dropna()

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
        
        # 2. Feature Engineering
        df_features = self._calculate_indicators(df)
        
        if df_features.empty:
            return "Neutral", 0.5
            
        # Select features for the LAST row (current market state)
        feature_cols = ['rsi', 'macd', 'signal', 'upper_bb', 'lower_bb', 'roc']
        last_row = df_features.iloc[[-1]][feature_cols]
        
        try:
            # 3. Predict Probability of Class 1 (UP)
            # predict_proba returns [[prob_0, prob_1]]
            probs = self.model.predict_proba(last_row)[0]
            prob_up = float(probs[1])
            
            # 4. Threshold Logic (0.6 / 0.4)
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