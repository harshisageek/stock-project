from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"

class MarketSignal(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    NEUTRAL = "Neutral"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"

class StockDataPoint(BaseModel):
    """Atomic OHLCV Data Point"""
    datetime: Union[datetime, str]
    open: float
    high: float
    low: float
    close: float
    volume: int

class Article(BaseModel):
    """News Article Model"""
    title: str
    link: str
    published: str
    publisher: str
    summary: Optional[str] = None
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TechnicalIndicators(BaseModel):
    rsi: Optional[float]
    sma: Optional[float]
    macd: Optional[float]
    bb_upper: Optional[float]
    bb_lower: Optional[float]

class AnalysisResult(BaseModel):
    """Final Output of the Brain"""
    ticker: str
    current_price: float
    sentiment_score: float
    technical_score: float
    final_score: float
    signal: MarketSignal
    confidence: float
    components: Dict[str, Any]
    articles: List[Article]
