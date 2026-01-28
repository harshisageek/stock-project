from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch

# Initialize FinBERT (Load once)
MODEL_NAME = "yiyanghkust/finbert-tone"

# Lazy Loading Singleton
_nlp_pipeline = None

def get_pipeline():
    global _nlp_pipeline
    if _nlp_pipeline is None:
        print("Lazy Loading FinBERT model... (First run only)", flush=True)
        try:
            tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
            model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
            # Use GPU if available for batch processing
            device = 0 if torch.cuda.is_available() else -1
            _nlp_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, top_k=None, device=device)
            print(f"FinBERT model loaded successfully on {'GPU' if device == 0 else 'CPU'}.", flush=True)
        except Exception as e:
            print(f"CRITICAL: Failed to load FinBERT: {e}", flush=True)
            return None
    return _nlp_pipeline

def analyze_sentiment_batch(texts: list) -> list:
    """
    Analyzes a list of strings in a single batch.
    Returns a list of float scores (-1.0 to 1.0).
    """
    if not texts:
        return []
        
    try:
        nlp = get_pipeline()
        if not nlp:
            return [0.0] * len(texts)
            
        # Clean and truncate texts
        cleaned_texts = [t[:1000] if (t and len(t.strip()) > 5) else "" for t in texts]
        
        # Batch inference
        results = nlp(cleaned_texts, truncation=True, max_length=512, batch_size=len(texts))
        
        scores = []
        for res in results:
            # res is a list of dicts like [{'label': 'Positive', 'score': 0.9}, ...]
            s_map = {item['label']: item['score'] for item in res}
            scores.append(s_map.get("Positive", 0.0) - s_map.get("Negative", 0.0))
            
        return scores
            
    except Exception as e:
        print(f"FinBERT Batch Error: {e}")
        return [0.0] * len(texts)

def analyze_sentiment(text: str) -> float:
    """
    Analyzes a single string. (Legacy wrapper for batch logic)
    """
    if not text or len(text.strip()) < 5:
        return 0.0
    return analyze_sentiment_batch([text])[0]