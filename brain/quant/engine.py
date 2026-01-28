"""
Quant Brain Engine - Technical Analysis Module
Generates Composite Trading Scores (-100 to +100) using RSI, SMA, MACD, and Sentiment.
"""

import pandas as pd
import numpy as np


class QuantEngine:
    """
    Core quantitative analysis engine for generating trading signals.
    
    Combines technical indicators (RSI, SMA, MACD) with sentiment analysis
    to produce a normalized composite trading score.
    """
    
    def __init__(self, data: list):
        """
        Initialize the Quant Engine with raw price data.
        
        Args:
            data: List of dictionaries containing OHLCV data.
                  Expected keys: 'datetime', 'open', 'high', 'low', 'close', 'volume'
        """
        self.raw_data = data
        self.df = None
        self.preprocess()
    
    def preprocess(self) -> pd.DataFrame:
        """
        Convert raw price data list to a Pandas DataFrame.
        
        Returns:
            Processed DataFrame with datetime index and numeric columns.
        """
        self.df = pd.DataFrame(self.raw_data)
        
        # Ensure numeric types for price columns
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Parse datetime if present
        if 'datetime' in self.df.columns:
            self.df['datetime'] = pd.to_datetime(self.df['datetime'])
            self.df.set_index('datetime', inplace=True)
        
        # Sort by datetime (oldest first for proper calculations)
        self.df.sort_index(inplace=True)
        
        return self.df
    
    def calc_rsi(self, period: int = 14) -> float:
        """
        Calculate the Relative Strength Index (RSI).
        
        RSI measures the speed and magnitude of recent price changes
        to evaluate overbought or oversold conditions.
        
        Args:
            period: Lookback period for RSI calculation (default: 14)
        
        Returns:
            RSI value between 0-100. Returns NaN if insufficient data.
        """
        if self.df is None or len(self.df) < period + 1:
            return np.nan
        
        # Calculate price changes
        delta = self.df['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0.0)
        losses = (-delta).where(delta < 0, 0.0)
        
        # Calculate exponential moving average of gains and losses
        avg_gain = gains.ewm(span=period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(span=period, min_periods=period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Return the most recent RSI value
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else np.nan
    
    def calc_sma(self, period: int = 50) -> float:
        """
        Calculate the Simple Moving Average (SMA).
        
        SMA is the arithmetic mean of prices over a specified period,
        used to identify trend direction.
        
        Args:
            period: Lookback period for SMA calculation (default: 50)
        
        Returns:
            SMA value. Returns NaN if insufficient data.
        """
        if self.df is None or len(self.df) < period:
            return np.nan
        
        sma = self.df['close'].rolling(window=period).mean()
        
        return float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else np.nan
    
    def calc_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
        # ... (Existing MACD implementation)
        if self.df is None or len(self.df) < slow + signal:
            return {'macd_line': np.nan, 'signal_line': np.nan, 'histogram': np.nan}
        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            'macd_line': float(macd_line.iloc[-1]),
            'signal_line': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    def calc_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> dict:
        """Calculates Upper and Lower Bollinger Bands."""
        if self.df is None or len(self.df) < period:
            return {'upper': np.nan, 'lower': np.nan, 'middle': np.nan}
        
        middle_band = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return {
            'upper': float(upper_band.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'middle': float(middle_band.iloc[-1])
        }

    def calculate_score(self, sentiment_score: float) -> dict:
        # ... (Previous code)
        current_price = float(self.df['close'].iloc[-1])
        rsi_val = self.calc_rsi()
        sma_val = self.calc_sma()
        bb = self.calc_bollinger_bands()
        
        # === Bollinger Band Score ===
        # Price > Upper Band = Overbought (-100)
        # Price < Lower Band = Oversold (+100)
        if pd.isna(current_price) or pd.isna(bb['upper']):
            bb_score = 0
        elif current_price > bb['upper']:
            bb_score = -100
        elif current_price < bb['lower']:
            bb_score = 100
        else:
            bb_score = 0
            
        # Re-balancing Weights: Sentiment (25%), Trend (35%), RSI (20%), BB (20%)
        sentiment_normalized = sentiment_score * 100
        trend_normalized = 100 if current_price > sma_val else -100
        rsi_normalized = 100 - ((rsi_val - 30) * 5) if not pd.isna(rsi_val) else 0
        
        final_score = (
            (0.25 * sentiment_normalized) +
            (0.35 * trend_normalized) +
            (0.20 * rsi_normalized) +
            (0.20 * bb_score)
        )
        
        # Clamp final score to [-100, 100]
        final_score = max(-100, min(100, final_score))
        
        # Get MACD Data
        macd_data = self.calc_macd()
        
        return {
            'final_score': round(final_score, 2),
            'breakdown': {
                'rsi_val': round(rsi_val, 2) if not pd.isna(rsi_val) else None,
                'rsi_normalized': round(rsi_normalized, 2),
                'sma_val': round(sma_val, 2) if not pd.isna(sma_val) else None,
                'trend_normalized': round(trend_normalized, 2),
                'current_price': round(current_price, 2) if not pd.isna(current_price) else None,
                'sentiment_input': round(sentiment_score, 4),
                'sentiment_normalized': round(sentiment_normalized, 2),
                'macd': {
                    'macd_line': round(macd_data['macd_line'], 4) if not pd.isna(macd_data['macd_line']) else None,
                    'signal_line': round(macd_data['signal_line'], 4) if not pd.isna(macd_data['signal_line']) else None,
                    'histogram': round(macd_data['histogram'], 4) if not pd.isna(macd_data['histogram']) else None
                }
            },
            'weights': {
                'sentiment': 0.3,
                'trend': 0.4,
                'rsi': 0.3
            }
        }
