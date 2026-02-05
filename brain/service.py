from typing import List, Dict, Any
from brain.core.types import AnalysisResult, StockDataPoint, Article, MarketSignal
from brain.core.config import BrainConfig
from brain.core.indicators import add_technical_indicators
from brain.prediction.engine import PredictionEngine
from brain.prediction.xgboost_engine import XGBoostPredictor
import pandas as pd

class BrainService:
    """
    The Central Nervous System.
    Orchestrates Technical Analysis, Sentiment Aggregation, Neural Prediction, and XGBoost Analysis.
    """
    def __init__(self):
        self.config = BrainConfig.get_instance()
        self.lstm_predictor = PredictionEngine()
        self.xgb_predictor = XGBoostPredictor()
        
    def analyze_ticker(self, 
                       ticker: str, 
                       history_data: List[StockDataPoint], 
                       sentiment_score: float, 
                       news_articles: List[Article]) -> AnalysisResult:
                       
        # 1. Technical Analysis (Centralized)
        # Convert to DataFrame
        records = [
            {
                'datetime': d.datetime, 
                'open': d.open, 
                'high': d.high, 
                'low': d.low, 
                'close': d.close, 
                'volume': d.volume
            } 
            for d in history_data
        ]
        df = pd.DataFrame(records)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)
        
        # Use centralized indicators
        # Note: We need to map lowercase keys to Title Case for indicators or handle it there.
        # Indicators expects 'Close' or 'close'.
        df = add_technical_indicators(df)
        
        # Extract latest values for logic
        current_price = df['close'].iloc[-1]
        rsi_val = df['RSI'].iloc[-1]
        sma_val = df['SMA_50'].iloc[-1]
        bb_upper = df['BB_Upper'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]
        macd_line = df['MACD'].iloc[-1]
        signal_line = df['MACD_Signal'].iloc[-1]
        hist = macd_line - signal_line
        
        # Calculate Scores
        bb_score = 0
        if current_price > bb_upper: bb_score = -100
        elif current_price < bb_lower: bb_score = 100
            
        trend_score = 100 if current_price > sma_val else -100
        
        rsi_score = 0
        if not pd.isna(rsi_val):
            rsi_score = 100 - ((rsi_val - 30) * 5)
            rsi_score = max(-100, min(100, rsi_score))
            
        # 2. AI Model Predictions (Ensemble)
        # A. LSTM
        lstm_signal, lstm_conf = self.lstm_predictor.predict(history_data)
        
        # B. XGBoost
        xgb_signal_str, xgb_prob = self.xgb_predictor.predict_probability(history_data)
        # Normalize XGB probability (0-1) to Score (-100 to 100)
        xgb_score = (xgb_prob - 0.5) * 200 
        
        # 3. Composite Score Calculation
        sentiment_normalized = sentiment_score * 100
        
        # --- ENSEMBLE WEIGHTING (Config Based) ---
        # Fallback to hardcoded if config missing (Safety)
        w_lstm = getattr(self.config, 'WEIGHT_LSTM', 0.30)
        w_xgb = getattr(self.config, 'WEIGHT_XGBOOST', 0.40)
        w_sent = getattr(self.config, 'WEIGHT_SENTIMENT', 0.20)
        w_trend = getattr(self.config, 'WEIGHT_TREND', 0.10)
        
        # Convert LSTM "Bullish"/"Bearish" to Score
        lstm_score = 75.0 if lstm_signal == "Bullish" else -75.0 if lstm_signal == "Bearish" else 0.0
        if lstm_signal != "Neutral":
            lstm_score = lstm_score * (lstm_conf + 0.5)
            
        # Amplify Quant Score
        xgb_score = xgb_score * 2.0
        xgb_score = max(-100, min(100, xgb_score))

        final_score = (
            (w_lstm * lstm_score) +
            (w_xgb * xgb_score) +
            (w_sent * sentiment_normalized) +
            (w_trend * (trend_score * 0.5))
        )
        
        final_score = max(-100, min(100, final_score))
        
        # 4. Generate Final Signal
        if final_score >= 50: signal = MarketSignal.STRONG_BUY
        elif final_score >= 15: signal = MarketSignal.BUY
        elif final_score <= -50: signal = MarketSignal.STRONG_SELL
        elif final_score <= -15: signal = MarketSignal.SELL
        else: signal = MarketSignal.NEUTRAL

        # --- DEEP QUANT LOGIC ---
        strategy = "Neutral / Hold"
        if rsi_score > 80: strategy = "Mean Reversion (Overbought)"
        elif rsi_score < -80: strategy = "Mean Reversion (Oversold)"
        elif trend_score > 70: strategy = "Momentum Trend Follow"
        elif trend_score < -70: strategy = "Bearish Trend Follow"
        elif sentiment_normalized > 60 and xgb_signal_str == "Bullish": strategy = "News-Quant Convergence"
        
        prices = [d.close for d in history_data[-30:]]
        support = min(prices) if prices else 0
        resistance = max(prices) if prices else 0
        
        inst_flow = "Neutral"
        if final_score > 30: inst_flow = "Accumulation Detected"
        elif final_score < -30: inst_flow = "Distribution Detected"

        # 5. Construct Result
        quant_components = {
            "technical": {
                "values": {
                    "current_price": current_price,
                    "rsi": rsi_val,
                    "sma": sma_val,
                    "macd": {"macd": macd_line, "signal": signal_line, "hist": hist},
                    "bollinger": {"upper": bb_upper, "lower": bb_lower}
                },
                "scores": {
                    "rsi": rsi_score,
                    "trend": trend_score,
                    "bb": bb_score
                }
            },
            "neural": {
                "signal": lstm_signal,
                "confidence": lstm_conf
            },
            "weights": {
                "lstm": w_lstm,
                "xgboost": w_xgb,
                "sentiment": w_sent,
                "trend": w_trend
            },
            "expert_opinion": {
                "xgboost": {
                    "signal": xgb_signal_str,
                    "score": round(xgb_score, 2),
                    "probability": round(xgb_prob * 100, 1)
                },
                "lstm": {
                    "signal": lstm_signal,
                    "confidence": round(lstm_conf * 100, 1)
                },
                "sentiment": {
                    "score": round((sentiment_normalized + 100) / 2, 1),
                    "label": "Bullish" if sentiment_normalized > 20 else "Bearish" if sentiment_normalized < -20 else "Neutral"
                }
            },
            "deep_insight": {
                "strategy": strategy,
                "support_level": support,
                "resistance_level": resistance,
                "institutional_flow": inst_flow,
                "signal_strength": abs(final_score)
            }
        }
        
        # Weighted Confidence
        xgb_conf = abs(xgb_prob - 0.5) * 2
        sent_conf = abs(sentiment_normalized) / 100
        trend_conf = abs(trend_score) / 100
        
        system_confidence = (
            (w_lstm * lstm_conf) +
            (w_xgb * xgb_conf) +
            (w_sent * sent_conf) +
            (w_trend * trend_conf)
        )

        return AnalysisResult(
            ticker=ticker,
            current_price=current_price,
            sentiment_score=sentiment_score,
            technical_score=final_score, 
            final_score=final_score,
            signal=signal,
            confidence=round(system_confidence, 4), 
            components=quant_components,
            articles=news_articles
        )
