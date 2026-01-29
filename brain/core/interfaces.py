from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .types import StockDataPoint, Article

class IDataProvider(ABC):
    @abstractmethod
    def fetch_history(self, ticker: str, range_str: str) -> List[StockDataPoint]:
        pass

class INewsProvider(ABC):
    @abstractmethod
    def fetch_news(self, ticker: str) -> List[Article]:
        pass

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        pass
