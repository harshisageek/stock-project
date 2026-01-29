import torch
import logging
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from typing import List, Optional
from brain.core.exceptions import ModelLoadException, AnalysisException

logger = logging.getLogger(__name__)

class SentimentEngine:
    """
    NLP Engine using FinBERT for sentiment analysis.
    Implements Lazy Loading and Batch Processing.
    """
    _pipeline = None
    _model_name = "yiyanghkust/finbert-tone"

    @classmethod
    def _load_model(cls):
        if cls._pipeline is not None:
            return

        logger.info("Initializing FinBERT model...")
        try:
            tokenizer = BertTokenizer.from_pretrained(cls._model_name)
            model = BertForSequenceClassification.from_pretrained(cls._model_name)
            
            # Device Selection
            device = -1 # CPU
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
                top_k=None # Return all scores
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
        
        # Pre-process: Truncate to ~1500 chars to avoid token limit issues (512 tokens)
        cleaned_texts = [t[:1500] if t else "" for t in texts]
        
        # Track valid indices to handle empty strings gracefully
        valid_indices = [i for i, t in enumerate(cleaned_texts) if t.strip()]
        valid_inputs = [cleaned_texts[i] for i in valid_indices]
        
        if not valid_inputs:
            return [0.0] * len(texts)
            
        try:
            # Batch Inference
            results = cls._pipeline(valid_inputs, truncation=True, max_length=512, batch_size=len(valid_inputs))
            
            final_scores = [0.0] * len(texts)
            
            for idx, res in zip(valid_indices, results):
                # res is [{'label': 'Positive', 'score': 0.9}, ...]
                scores = {item['label']: item['score'] for item in res}
                
                # Composite Score: Positive - Negative
                composite = scores.get("Positive", 0.0) - scores.get("Negative", 0.0)
                
                # Dampen to avoid extreme 1.0/-1.0 scores (User Feedback)
                composite = composite * 0.95
                
                final_scores[idx] = round(composite, 4)
                
            return final_scores
            
        except Exception as e:
            logger.error(f"Sentiment Batch Error: {e}")
            raise AnalysisException(f"Sentiment analysis failed: {e}")

    @classmethod
    def analyze_one(cls, text: str) -> float:
        return cls.analyze_batch([text])[0]
