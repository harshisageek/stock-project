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
            _nlp_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, top_k=None)
            print("FinBERT model loaded successfully.", flush=True)
        except Exception as e:
            print(f"Failed to load FinBERT: {e}", flush=True)
            return None
    return _nlp_pipeline

def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of text using FinBERT.
    Returns composite score: Prob(Positive) - Prob(Negative).
    Range: -1.0 to 1.0.
    """
    if not text or len(text.strip()) < 5:
        return 0.0
        
    try:
        nlp = get_pipeline()
        if not nlp:
            return 0.0
            
        # FinBERT input limit is 512 tokens. truncated=True handles this.
        results = nlp(text[:2000], truncation=True, max_length=512)
        # Result format: [[{'label': 'Neutral', 'score': 0.8}, {'label': 'Positive', 'score': 0.1}, ...]]
        # Note: pipeline with top_k=None returns a list of lists (for batches) or just list (if single).
        # We need to handle the structure carefully.
        
        scores = {}
        # Flatten input if needed
        dataset = results[0] if isinstance(results[0], list) else results
        
        for item in dataset:
            scores[item['label']] = item['score']
            
        # Calculate composite score
        pos = scores.get("Positive", 0.0)
        neg = scores.get("Negative", 0.0)
        
        # Neutral doesn't contribute directly to direction, but dilutes the magnitude naturally 
        # because pos + neg + neu = 1.
        
        sentiment_score = pos - neg
        return sentiment_score
            
    except Exception as e:
        print(f"FinBERT Error: {e}")
        return 0.0
