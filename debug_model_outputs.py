import torch
import numpy as np
import pickle
import pandas as pd
from brain.neural_networks.model import StockLSTM

def check_model_outputs():
    # 1. Load Data
    try:
        data = np.load("brain/saved_models/training_cache.npz")
        x_val = data['x_val'] # Shape: (N, 60, 15)
        y_val = data['y_val'] # Shape: (N,) - This is already Z-Scored!
    except Exception as e:
        print(f"Error loading cache: {e}")
        return

    # 2. Load Scaler Stats to Un-Scale Targets/Preds
    try:
        with open("brain/saved_models/scaler.pkl", "rb") as f:
            scaler_data = pickle.load(f)
            t_mean = scaler_data.get('mean', 0.0)
            t_std = scaler_data.get('std', 1.0)
            print(f"Loaded Scaler Stats -> Mean: {t_mean:.4f}, Std: {t_std:.4f}")
    except Exception as e:
        print(f"Error loading scaler: {e}")
        t_mean, t_std = 0.0, 1.0

    # 3. Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = StockLSTM(input_size=17).to(device)
    
    try:
        state = torch.load("brain/saved_models/hybrid_lstm.pth", map_location=device)
        model.load_state_dict(state)
        model.eval()
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print(f"--- Debugging Model Predictions (Device: {device}) ---")
    
    # 4. Predict on a random sample of 20 items
    indices = np.random.choice(len(x_val), 20, replace=False)
    
    sample_x = torch.FloatTensor(x_val[indices]).to(device)
    sample_y_z = y_val[indices] # Z-Score targets
    
    with torch.no_grad():
        preds_z = model(sample_x).cpu().numpy().flatten()
    
    # 5. Show Side-by-Side (Un-scaled)
    print(f"{'True Return %':<15} | {'Predicted %':<15} | {'Diff %':<15}")
    print("-" * 50)
    
    true_raw_values = []
    pred_raw_values = []
    
    for y_z, p_z in zip(sample_y_z, preds_z):
        # Un-scale
        y_raw = (y_z * t_std) + t_mean
        p_raw = (p_z * t_std) + t_mean
        
        true_raw_values.append(y_raw)
        pred_raw_values.append(p_raw)
        
        diff = abs(y_raw - p_raw)
        print(f"{y_raw:<15.4f} | {p_raw:<15.4f} | {diff:<15.4f}")

    print("-" * 50)
    print(f"Mean True Abs Value: {np.mean(np.abs(true_raw_values)):.4f}")
    print(f"Mean Pred Abs Value: {np.mean(np.abs(pred_raw_values)):.4f}")
    
    if np.std(pred_raw_values) < 0.1:
        print("\n[DIAGNOSIS]: MODEL COLLAPSE DETECTED (Predictions are flat).")
    else:
        print("\n[DIAGNOSIS]: Model is making varied predictions.")

if __name__ == "__main__":
    check_model_outputs()
