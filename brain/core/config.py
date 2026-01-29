import os

class BrainConfig:
    """Centralized Configuration for the Brain Module"""
    
    # Weights for the composite score
    WEIGHT_SENTIMENT: float = 0.25
    WEIGHT_TREND: float = 0.35
    WEIGHT_RSI: float = 0.20
    WEIGHT_BB: float = 0.20
    
    # Thresholds
    RSI_OVERBOUGHT: int = 70
    RSI_OVERSOLD: int = 30
    
    # Model Paths
    # Using relative paths assuming execution from project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # brain/
    MODEL_PATH: str = os.path.join(BASE_DIR, "saved_models", "hybrid_lstm.pth")
    SCALER_PATH: str = os.path.join(BASE_DIR, "saved_models", "scaler.pkl")
    
    # API Limits
    MAX_NEWS_ARTICLES: int = 20
    SENTIMENT_THRESHOLD: float = 0.05
    
    @classmethod
    def get_instance(cls):
        return cls()
