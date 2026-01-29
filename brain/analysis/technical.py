import pandas as pd
import numpy as np
from typing import List, Dict, Any
from brain.core.types import StockDataPoint
from brain.core.config import BrainConfig

class TechnicalAnalyzer:
    """
    Industry-grade Technical Analysis Engine.
    Uses Pandas for vectorized calculations.
    """
    
    def __init__(self, data: List[StockDataPoint]):
        # Fast conversion from Pydantic models to DataFrame
        if not data:
            self.df = pd.DataFrame()
            return
            
        # Optimize: model_dump() can be slow for large lists. 
        # Accessing attributes directly is faster.
        records = [
            {
                'datetime': d.datetime, 
                'open': d.open, 
                'high': d.high, 
                'low': d.low, 
                'close': d.close, 
                'volume': d.volume
            } 
            for d in data
        ]
        
        self.df = pd.DataFrame(records)
        
        if not self.df.empty:
            self.df['datetime'] = pd.to_datetime(self.df['datetime'])
            self.df.set_index('datetime', inplace=True)
            self.df.sort_index(inplace=True)
            
            # Ensure floats
            cols = ['open', 'high', 'low', 'close']
            for c in cols:
                self.df[c] = self.df[c].astype(float)

    def _calc_rsi(self, period: int = 14) -> float:
        if self.df.empty or len(self.df) < period + 1:
            return np.nan
            
        delta = self.df['close'].diff()
        gains = delta.where(delta > 0, 0.0)
        losses = (-delta).where(delta < 0, 0.0)
        
        avg_gain = gains.ewm(span=period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(span=period, min_periods=period, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1])

    def _calc_sma(self, period: int = 50) -> float:
        if self.df.empty or len(self.df) < period:
            return np.nan
        return float(self.df['close'].rolling(window=period).mean().iloc[-1])

    def _calc_macd(self, fast=12, slow=26, signal=9) -> Dict[str, float]:
        if self.df.empty or len(self.df) < slow + signal:
            return {'macd': np.nan, 'signal': np.nan, 'hist': np.nan}
            
        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        hist = macd_line - signal_line
        
        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'hist': float(hist.iloc[-1])
        }

    def _calc_bollinger(self, period=20, std_dev=2) -> Dict[str, float]:
        if self.df.empty or len(self.df) < period:
            return {'upper': np.nan, 'lower': np.nan, 'middle': np.nan}
            
        middle = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()
        
        return {
            'upper': float((middle + (std * std_dev)).iloc[-1]),
            'lower': float((middle - (std * std_dev)).iloc[-1]),
            'middle': float(middle.iloc[-1])
        }

    def analyze(self) -> Dict[str, Any]:
        """
        Runs all technical indicators and returns raw values + partial scores.
        """
        if self.df.empty:
            return {}

        current_price = float(self.df['close'].iloc[-1])
        rsi = self._calc_rsi()
        sma = self._calc_sma()
        bb = self._calc_bollinger()
        macd = self._calc_macd()

        # Score Logic (Ported and Cleaned)
        # 1. BB Score
        bb_score = 0
        if not np.isnan(bb['upper']):
            if current_price > bb['upper']: bb_score = -100
            elif current_price < bb['lower']: bb_score = 100
        
        # 2. Trend Score
        trend_score = 0
        if not np.isnan(sma):
            trend_score = 100 if current_price > sma else -100
            
        # 3. RSI Score (Normalize 30-70 range to score)
        # RSI 30 -> 100 score, RSI 70 -> -100 score?
        # Original logic: 100 - ((rsi - 30) * 5)
        # If RSI=30: 100 - (0) = 100 (Buy)
        # If RSI=70: 100 - (200) = -100 (Sell)
        # If RSI=50: 100 - (100) = 0 (Neutral)
        rsi_score = 0
        if not np.isnan(rsi):
            rsi_score = 100 - ((rsi - 30) * 5)
            # Clamp
            rsi_score = max(-100, min(100, rsi_score))

        return {
            "values": {
                "current_price": current_price,
                "rsi": rsi,
                "sma": sma,
                "macd": macd,
                "bollinger": bb
            },
            "scores": {
                "bb": bb_score,
                "trend": trend_score,
                "rsi": rsi_score
            }
        }
