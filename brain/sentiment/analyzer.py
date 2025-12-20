from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of text using VADER.
    
    Args:
        text: Text to analyze
        
    Returns:
        Compound sentiment score from -1 (negative) to 1 (positive)
    """
    scores = sentiment_analyzer.polarity_scores(text)
    return scores["compound"]
