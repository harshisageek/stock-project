import numpy as np
import xgboost as xgb
import pickle
import os
from sklearn.metrics import confusion_matrix

def check_xgboost_outputs():
    # 1. Load Data
    try:
        data = np.load("brain/saved_models/training_cache.npz")
        x_val_seq = data['x_val'] 
        y_val = data['y_val']   # Class Targets (0, 1, 2)
        
        # Flatten input for XGBoost (Take last step of sequence)
        x_val = x_val_seq[:, -1, :] 
    except Exception as e:
        print(f"Error loading cache: {e}")
        return

    # 2. Load Model
    if not os.path.exists("brain/saved_models/xgboost_model.json"):
        print("XGBoost model not found.")
        return

    model = xgb.XGBClassifier()
    model.load_model("brain/saved_models/xgboost_model.json")

    print(f"--- Large Batch Validation (10,000 samples) ---")
    
    # 3. Predict on a LARGE random sample
    sample_size = 10000
    if len(x_val) < sample_size:
        sample_size = len(x_val)
        
    indices = np.random.choice(len(x_val), sample_size, replace=False)
    
    sample_x = x_val[indices]
    sample_y = y_val[indices]
    
    preds = model.predict(sample_x)
    
    # 4. Statistics
    acc = np.mean(preds == sample_y) * 100
    print(f"\nAccuracy: {acc:.2f}% (Baseline Random: 33.3%)")
    
    # 5. Confusion Matrix
    # Rows: True, Cols: Predicted
    cm = confusion_matrix(sample_y, preds, labels=[0, 1, 2])
    
    print("\nConfusion Matrix:")
    print(f"{'':<10} | {'Pred Sell':<10} | {'Pred Hold':<10} | {'Pred Buy':<10}")
    print("-" * 50)
    print(f"{'True Sell':<10} | {cm[0][0]:<10} | {cm[0][1]:<10} | {cm[0][2]:<10}")
    print(f"{'True Hold':<10} | {cm[1][0]:<10} | {cm[1][1]:<10} | {cm[1][2]:<10}")
    print(f"{'True Buy':<10} | {cm[2][0]:<10} | {cm[2][1]:<10} | {cm[2][2]:<10}")
    
    # 6. Detailed Precision (When we predict Buy, are we right?)
    sell_prec = cm[0][0] / (cm[0][0] + cm[1][0] + cm[2][0] + 1e-6) * 100
    buy_prec = cm[2][2] / (cm[0][2] + cm[1][2] + cm[2][2] + 1e-6) * 100
    
    print("-" * 50)
    print(f"Sell Precision: {sell_prec:.2f}% (When model says Sell, is it right?)")
    print(f"Buy Precision:  {buy_prec:.2f}% (When model says Buy, is it right?)")

if __name__ == "__main__":
    check_xgboost_outputs()