
import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "yiyanghkust/finbert-tone"

# Singleton Storage
_nlp_pipeline = None

def get_pipeline():
    """
    Lazy loads the FinBERT pipeline.
    Returns None if loading fails.
    """
    global _nlp_pipeline
    if _nlp_pipeline is None:
        logger.info("Initializing FinBERT model (Lazy Load)...")
        try:
            tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
            model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
            
            # Auto-detect device: CUDA > MPS (Mac) > CPU
            if torch.cuda.is_available():
                device = 0 
                logger.info(f"FinBERT loading on GPU: {torch.cuda.get_device_name(0)}")
            elif torch.backends.mps.is_available():
                device = "mps" 
                logger.info("FinBERT loading on MPS (Apple Silicon)")
            else:
                device = -1
                logger.info("FinBERT loading on CPU")

            _nlp_pipeline = pipeline(
                "sentiment-analysis", 
                model=model, 
                tokenizer=tokenizer, 
                top_k=None, 
                device=device
            )
            logger.info("FinBERT initialized successfully.")
            
        except Exception as e:
            logger.critical(f"Failed to load FinBERT: {e}")
            return None
            
    return _nlp_pipeline

def analyze_sentiment_batch(texts: list[str]) -> list[float]:
    """
    Analyzes a batch of text strings using FinBERT.
    
    Args:
        texts: List of strings to analyze.
        
    Returns:
        List of sentiment scores (-1.0 to 1.0).
        Positive > 0, Negative < 0.
    """
    if not texts:
        return []
        
    nlp = get_pipeline()
    if not nlp:
        # Fallback if model fails
        return [0.0] * len(texts)
        
    # Pre-processing: Truncate to avoid BERT token limit errors (512 tokens approx)
    # We truncate char length to ~1500 to be safe before tokenization
    cleaned_texts = [t[:1500] if t else "" for t in texts]
    
    # Filter out empty strings to prevent pipeline errors, track their indices
    valid_indices = [i for i, t in enumerate(cleaned_texts) if t.strip()]
    valid_inputs = [cleaned_texts[i] for i in valid_indices]
    
    if not valid_inputs:
        return [0.0] * len(texts)
    
    try:
        # Batch Inference
        # set truncation=True to handle edge cases explicitly
        results = nlp(valid_inputs, truncation=True, max_length=512, batch_size=len(valid_inputs))
        
        # Map results back to original order
        final_scores = [0.0] * len(texts)
        
        for idx, res in zip(valid_indices, results):
            # res is list of dicts: [{'label': 'Positive', 'score': 0.99}, {'label': 'Negative', 'score': 0.01}, ...]
            scores = {item['label']: item['score'] for item in res}
            
            # Composite Score: Positive - Negative (Neutral is ignored/implicit)
            # Range: -1.0 (Pure Negative) to +1.0 (Pure Positive)
            composite = scores.get("Positive", 0.0) - scores.get("Negative", 0.0)
            final_scores[idx] = composite
            
        return final_scores
        
    except Exception as e:
        logger.error(f"Sentiment Analysis Batch Error: {e}")
        return [0.0] * len(texts)

def analyze_sentiment(text: str) -> float:
    """
    Single text wrapper for batch analysis.
    """
    if not text or not text.strip():
        return 0.0
    return analyze_sentiment_batch([text])[0]
