
import logging
from brain.prediction.engine import PredictionEngine
from brain.core.types import StockDataPoint
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)

def generate_mock_history(days=100):
    history = []
    base_price = 150.0
    now = datetime.now()
    
    for i in range(days):
        date = now - timedelta(days=days-i)
        # Random walk
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        open_p = close * (1 + random.uniform(-0.01, 0.01))
        high = max(open_p, close) * (1 + random.uniform(0, 0.01))
        low = min(open_p, close) * (1 - random.uniform(0, 0.01))
        volume = int(random.uniform(1000000, 5000000))
        
        history.append(StockDataPoint(
            datetime=date,
            open=open_p,
            high=high,
            low=low,
            close=close,
            volume=volume
        ))
        base_price = close
        
    return history

def test_neural_network():
    print("--- TESTING NEURAL NETWORK ---")
    
    engine = PredictionEngine()
    
    # 1. Check Resources
    print("Loading resources...")
    engine._load_resources()
    
    if not engine._loaded:
        print("FAIL: Model not loaded. Check path: brain/saved_models/hybrid_lstm.pth")
        print("FAIL: Scaler path: brain/saved_models/scaler.pkl")
        return

    # 2. Generate Data
    data = generate_mock_history(days=100)
    print(f"Generated {len(data)} days of mock data.")
    
    # 3. Test Prepare Data
    print("Preparing data...")
    tensor = engine.prepare_data(data)
    
    if tensor is None:
        print("FAIL: prepare_data returned None.")
    else:
        print(f"PASS: Data prepared. Shape: {tensor.shape}")
        
    # 4. Predict
    print("Running prediction...")
    signal, conf = engine.predict(data)
    
    print(f"Result -> Signal: {signal}, Confidence: {conf}")
    
    if conf == 0.0:
        print("FAIL: Confidence is 0.0!")
    else:
        print("PASS: Non-zero confidence.")

if __name__ == "__main__":
    test_neural_network()
