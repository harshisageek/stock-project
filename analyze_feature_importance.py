import torch
import numpy as np
import xgboost as xgb
import pandas as pd
import os
import sys
from brain.neural_networks.model import StockLSTM

# Configuration
CACHE_FILE = "brain/saved_models/training_cache.npz"
XGB_MODEL_PATH = "brain/saved_models/xgboost_model.json"
LSTM_MODEL_PATH = "brain/saved_models/hybrid_lstm.pth"
FEATURE_NAMES = [
    'Log_Ret', 'RSI', 'MACD', 'MACD_Signal', 
    'BB_Pct', 'Vol_Ratio', 'ROC', 
    'SMA_Ratio', 'ATR_Pct', 'CCI', 
    'Ret_1d', 'Ret_3d', 'Ret_5d', 'Ret_10d', 'Ret_20d',
    'Sentiment', 'NewsVol'
]

def analyze_xgboost():
    print("\n--- XGBoost Feature Importance (Gain) ---")
    if not os.path.exists(XGB_MODEL_PATH):
        print("XGBoost model not found.")
        return

    # Updated to Classifier
    model = xgb.XGBClassifier()
    model.load_model(XGB_MODEL_PATH)
    
    importance = model.feature_importances_
    
    df = pd.DataFrame({
        'Feature': FEATURE_NAMES,
        'Importance': importance
    })
    
    df = df.sort_values(by='Importance', ascending=False).reset_index(drop=True)
    print(df)
    
    dead_feats = df[df['Importance'] < 0.01]['Feature'].tolist()
    if dead_feats:
        print(f"\n[WARNING] XGBoost is ignoring these features: {dead_feats}")

def analyze_lstm(x_val, y_val):
    print("\n--- LSTM Permutation Importance (Validation Set) ---")
    if not os.path.exists(LSTM_MODEL_PATH):
        print("LSTM model not found.")
        return

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = StockLSTM(input_size=len(FEATURE_NAMES), hidden_size=128).to(device)
    
    try:
        state = torch.load(LSTM_MODEL_PATH, map_location=device)
        model.load_state_dict(state)
        model.eval()
    except Exception as e:
        print(f"Error loading LSTM: {e}")
        return

    # 1. Calculate Baseline Accuracy
    limit = 5000 
    x_sample = torch.FloatTensor(x_val[:limit]).to(device)
    y_sample = torch.LongTensor(y_val[:limit]).to(device)
    
    with torch.no_grad():
        out = model(x_sample)
        _, preds = torch.max(out, 1)
        baseline_acc = (preds == y_sample).float().mean().item()
    
    print(f"Baseline Accuracy: {baseline_acc*100:.2f}%")
    
    # 2. Permute each feature
    results = []
    
    for i, feat_name in enumerate(FEATURE_NAMES):
        x_permuted = x_sample.clone()
        col = x_permuted[:, :, i]
        idx = torch.randperm(col.size(0))
        x_permuted[:, :, i] = col[idx, :]
        
        with torch.no_grad():
            out = model(x_permuted)
            _, preds = torch.max(out, 1)
            acc = (preds == y_sample).float().mean().item()
            
        # Importance = Drop in Accuracy
        impact = baseline_acc - acc
        results.append({'Feature': feat_name, 'Acc_Drop': impact})

    df = pd.DataFrame(results)
    df = df.sort_values(by='Acc_Drop', ascending=False).reset_index(drop=True)
    print(df)
    
    print("\n[INTERPRETATION]")
    print("Higher 'Acc_Drop' = Feature is crucial.")
    print("Zero or Negative = Feature is useless or noise.")

def main():
    if not os.path.exists(CACHE_FILE):
        print("Data cache not found.")
        return

    print(f"Loading data from {CACHE_FILE}...")
    with np.load(CACHE_FILE) as data:
        x_val = data['x_val']
        y_val = data['y_val']

    analyze_xgboost()
    analyze_lstm(x_val, y_val)

if __name__ == "__main__":
    main()
