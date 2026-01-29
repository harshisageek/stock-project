from typing import List, Dict, Any
from brain.core.types import AnalysisResult, StockDataPoint, Article, MarketSignal
from brain.core.config import BrainConfig
from brain.analysis.technical import TechnicalAnalyzer
from brain.prediction.engine import PredictionEngine
from brain.prediction.xgboost_engine import XGBoostPredictor

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
                       
        # 1. Technical Analysis
        ta_engine = TechnicalAnalyzer(history_data)
        ta_results = ta_engine.analyze()
        
        # 2. AI Model Predictions (Ensemble)
        # A. LSTM (Pattern Recognition)
        lstm_signal, lstm_conf = self.lstm_predictor.predict(history_data)
        
        # B. XGBoost (Quant Rules)
        xgb_signal_str, xgb_prob = self.xgb_predictor.predict_probability(history_data)
        # Normalize XGB probability (0-1) to Score (-100 to 100)
        xgb_score = (xgb_prob - 0.5) * 200 
        
        # 3. Composite Score Calculation
        scores = ta_results.get("scores", {})
        rsi_score = scores.get("rsi", 0)
        trend_score = scores.get("trend", 0)
        
        # Normalize Sentiment (-1 to 1) -> (-100 to 100)
        sentiment_normalized = sentiment_score * 100
        
        # --- ENSEMBLE WEIGHTING ---
        # Weights: LSTM (30%), XGBoost (30%), Sentiment (20%), Technical Trend (20%)
        # This is a robust "Board of Advisors" mix.
        
        # Convert LSTM "Bullish"/"Bearish" to Score
        lstm_score = 50.0 if lstm_signal == "Bullish" else -50.0 if lstm_signal == "Bearish" else 0.0
        if lstm_signal != "Neutral":
            lstm_score = lstm_score * (lstm_conf + 0.5) # Boost by confidence
            
        final_score = (
            (0.30 * lstm_score) +
            (0.30 * xgb_score) +
            (0.20 * sentiment_normalized) +
            (0.20 * trend_score)
        )
        
        # Clamp
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
        current_price = ta_results.get("values", {}).get("current_price", 0.0)
        
        quant_components = {
            "technical": ta_results,
            "neural": {
                "signal": lstm_signal,
                "confidence": lstm_conf
            },
            "weights": {
                "lstm": 0.30,
                "xgboost": 0.30,
                "sentiment": 0.20,
                "trend": 0.20
            },
            # NEW: Expert Opinion Breakdown for UI
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
                    "score": round(sentiment_normalized, 2),
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
        
        return AnalysisResult(
            ticker=ticker,
            current_price=current_price,
            sentiment_score=sentiment_score,
            technical_score=final_score, 
            final_score=final_score,
            signal=signal,
            confidence=max(lstm_conf, abs(xgb_prob - 0.5)*2), 
            components=quant_components,
            articles=news_articles
        )