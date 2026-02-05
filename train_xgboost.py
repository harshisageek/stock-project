import numpy as np
import xgboost as xgb
import os
import logging
from sklearn.metrics import accuracy_score

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_FILE = "brain/saved_models/training_cache.npz"
MODEL_PATH = "brain/saved_models/xgboost_model.json"

def train_xgboost():
    print("--- Starting XGBoost Training ---")
    
    # 1. Load Data
    if not os.path.exists(CACHE_FILE):
        print(f"Error: Cache file {CACHE_FILE} not found. Run train_production.py first.")
        return

    print(f"Loading data from {CACHE_FILE}...")
    with np.load(CACHE_FILE) as data:
        x_train_seq = data['x_train']
        y_train = data['y_train']
        x_val_seq = data['x_val']
        y_val = data['y_val']
        
    print(f"LSTM Train Shape: {x_train_seq.shape}")
    
    # 2. Flatten Sequence (Take last row)
    X_train = x_train_seq[:, -1, :]
    X_val = x_val_seq[:, -1, :]
    
    print(f"XGBoost Train Shape: {X_train.shape}")
    print(f"XGBoost Val Shape: {X_val.shape}")
    
    # 3. Initialize Model
    # Classification: 3 Classes (Sell, Hold, Buy)
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=3, 
        learning_rate=0.01,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_alpha=1.0,
        reg_lambda=5.0,
        gamma=0.1,
        objective='multi:softprob',
        num_class=3,
        eval_metric='mlogloss'
    )
    
    # 4. Train
    print("Training XGBoost Classifier...")
    
    model.fit(
        X_train, 
        y_train, 
        eval_set=[(X_val, y_val)], 
        verbose=True
    )
    
    # 5. Evaluate
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds) * 100
    
    print(f"--- XGBoost Validation Accuracy: {acc:.2f}% ---")
    
    # 6. Save
    model.save_model(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_xgboost()