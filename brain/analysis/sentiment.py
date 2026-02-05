import torch
import logging
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from typing import List, Optional
from threading import Lock
from brain.core.exceptions import ModelLoadException, AnalysisException

logger = logging.getLogger(__name__)

class SentimentEngine:
    """
    NLP Engine using FinBERT for sentiment analysis.
    Thread-safe Singleton implementation.
    """
    _pipeline = None
    _model_name = "yiyanghkust/finbert-tone"
    _lock = Lock() # Thread Safety

    @classmethod
    def _load_model(cls):
        # Double-checked locking pattern
        if cls._pipeline is not None:
            return

        with cls._lock:
            if cls._pipeline is not None:
                return

            logger.info("Initializing FinBERT model...")
            try:
                tokenizer = BertTokenizer.from_pretrained(cls._model_name)
                model = BertForSequenceClassification.from_pretrained(cls._model_name)
                
                device = -1 
                if torch.cuda.is_available():
                    device = 0
                    logger.info(f"FinBERT: Using GPU ({torch.cuda.get_device_name(0)})")
                elif torch.backends.mps.is_available():
                    device = "mps"
                    logger.info("FinBERT: Using MPS (Apple Silicon)")
                else:
                    logger.info("FinBERT: Using CPU")

                cls._pipeline = pipeline(
                    "sentiment-analysis", 
                    model=model, 
                    tokenizer=tokenizer, 
                    device=device,
                    top_k=None 
                )
                
            except Exception as e:
                logger.critical(f"FinBERT Load Failed: {e}")
                raise ModelLoadException(f"Could not load FinBERT: {e}")

    @classmethod
    def analyze_batch(cls, texts: List[str]) -> List[float]:
        """
        Analyzes a batch of texts.
        Returns sentiment scores from -1.0 (Negative) to 1.0 (Positive).
        """
        if not texts:
            return []
            
        cls._load_model()
        
        cleaned_texts = [t[:1500] if t else "" for t in texts]
        
        valid_indices = [i for i, t in enumerate(cleaned_texts) if t.strip()]
        valid_inputs = [cleaned_texts[i] for i in valid_indices]
        
        if not valid_inputs:
            return [0.0] * len(texts)
            
        try:
            results = cls._pipeline(valid_inputs, truncation=True, max_length=512, batch_size=len(valid_inputs))
            
            final_scores = [0.0] * len(texts)
            
            for idx, res in zip(valid_indices, results):
                scores = {item['label']: item['score'] for item in res}
                composite = scores.get("Positive", 0.0) - scores.get("Negative", 0.0)
                composite = composite * 0.95
                final_scores[idx] = round(composite, 4)
                
            return final_scores
            
        except Exception as e:
            logger.error(f"Sentiment Batch Error: {e}")
            raise AnalysisException(f"Sentiment analysis failed: {e}")

    @classmethod
    def analyze_one(cls, text: str) -> float:
        return cls.analyze_batch([text])[0]