import time
import numpy as np
import sys
import os
import pandas as pd
from dotenv import load_dotenv
from brain.neural_networks.data_processor import DataProcessor
from brain.neural_networks.trainer import ModelTrainer

load_dotenv()

TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD", 
    "INTC", "QCOM", "CRM", "ADBE", "NFLX", "CSCO", "AVGO", "TXN", 
    "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", 
    "PG", "KO", "PEP", "COST", "WMT", "TGT", "HD", "MCD", "NKE", 
    "SBUX", "DIS", "CMCSA", "VZ", "T", "TMUS", "XOM", "CVX", "COP", 
    "SLB", "PFE", "JNJ", "MRK", "ABBV", "LLY", "AMGN", "GILD", "UNH", 
    "ELV", "CVS", "BA", "CAT", "DE", "GE", "MMM", "HON", "IBM", 
    "ORCL", "ACN", "NOW"
]

CACHE_FILE = "brain/saved_models/training_cache.npz"

def fetch_and_aggregate():
    processor = DataProcessor()
    
    # We now collect RAW features + Targets, then Scale Globally
    raw_train_feats = []
    raw_val_feats = []
    train_targets = []
    val_targets = []
    
    batch_size = 8
    total_tickers = len(TICKERS)
    
    print(f"--- Live Fetch (Regression) ---")

    for i in range(0, total_tickers, batch_size):
        batch = TICKERS[i:i+batch_size]
        for ticker in batch:
            try:
                # We need a custom method to get RAW data, or we adjust prepare_ticker_data.
                # Since we can't easily change the class method without breaking other things,
                # we will manually fetch and process here for maximum control.
                
                df = processor.fetch_stock_history(ticker)
                if df is None: continue
                
                from brain.core.indicators import add_technical_indicators
                df = add_technical_indicators(df)
                
                # Target: 5-Day Forward Return Z-Score
                horizon = 5
                df['Future_Return'] = np.log(df['Close'].shift(-horizon) / df['Close'])
                
                ret_mean = df['Future_Return'].mean()
                ret_std = df['Future_Return'].std()
                df['Target'] = (df['Future_Return'] - ret_mean) / (ret_std + 1e-6)
                
                df['Sentiment'] = 0.0
                df['NewsVol'] = 0.0
                
                df = df.replace([np.inf, -np.inf], np.nan).dropna()
                
                split_idx = int(0.8 * len(df))
                gap = processor.sequence_length + horizon
                
                train_df = df.iloc[:split_idx - gap]
                val_df = df.iloc[split_idx:]
                
                if len(train_df) < processor.sequence_length: continue
                
                raw_train_feats.append(train_df[processor.FEATURE_COLS].values)
                raw_val_feats.append(val_df[processor.FEATURE_COLS].values)
                train_targets.append(train_df['Target'].values)
                val_targets.append(val_df['Target'].values)
                
                print(f"Fetched {ticker}")
            except Exception as e:
                print(f"Error {ticker}: {e}")

        if i + batch_size < total_tickers:
            print("Cooling down 70s...")
            time.sleep(70)

    if not raw_train_feats: raise ValueError("No data")

    # 1. Concatenate all RAW data
    all_train_feats = np.concatenate(raw_train_feats, axis=0)
    all_val_feats = np.concatenate(raw_val_feats, axis=0)
    
    all_train_targets = np.concatenate(train_targets, axis=0)
    all_val_targets = np.concatenate(val_targets, axis=0)

    # 2. Fit Scaler Globally
    print("Fitting Global Scaler...")
    processor.scaler.fit(all_train_feats)
    
    # 3. Transform
    scaled_train = processor.scaler.transform(all_train_feats)
    scaled_val = processor.scaler.transform(all_val_feats)
    
    # 4. Create Sequences (This is tricky with concatenated data)
    # We actually need to sequence-ize BEFORE concatenation or handle boundaries.
    # The previous approach of concatenating raw arrays destroyed the time boundaries between tickers.
    # To do this right: We must scale first, THEN sequence-ize per ticker.
    
    # RESTARTING STRATEGY:
    # 1. Collect all DFs.
    # 2. Fit Scaler on all Train DFs.
    # 3. Iterate again, transform each DF, make sequences, append.
    
    return None, None, None, None # Signal to retry logic below

def fetch_and_process_correctly():
    processor = DataProcessor()
    
    batch_size = 8
    total_tickers = len(TICKERS)
    
    all_train_dfs = []
    all_val_dfs = []
    
    print("--- Phase 1: Fetching Data ---")
    for i in range(0, total_tickers, batch_size):
        batch = TICKERS[i:i+batch_size]
        for ticker in batch:
            try:
                df = processor.fetch_stock_history(ticker)
                if df is None: continue
                
                from brain.core.indicators import add_technical_indicators
                df = add_technical_indicators(df)
                
                # Target: 3-Class Classification
                horizon = 5
                future_ret = (df['Close'].shift(-horizon) / df['Close'] - 1) * 100
                
                # 0=Sell (< -1.5%), 1=Hold, 2=Buy (> 1.5%)
                conditions = [(future_ret < -1.5), (future_ret > 1.5)]
                choices = [0, 2]
                df['Target_Class'] = np.select(conditions, choices, default=1)
                
                df['Sentiment'] = 0.0
                df['NewsVol'] = 0.0
                
                df = df.replace([np.inf, -np.inf], np.nan).dropna()
                
                split_idx = int(0.8 * len(df))
                gap = processor.sequence_length + horizon
                
                train_df = df.iloc[:split_idx - gap].copy()
                val_df = df.iloc[split_idx:].copy()
                
                if len(train_df) < processor.sequence_length: continue
                
                all_train_dfs.append(train_df)
                all_val_dfs.append(val_df)
                print(f"Loaded {ticker}")
                
            except Exception as e:
                print(f"Error {ticker}: {e}")
        
        if i + batch_size < total_tickers:
            time.sleep(70)
            
    # Phase 2: Global Scaling (Features Only)
    print("--- Phase 2: Global Scaling ---")
    if not all_train_dfs: raise ValueError("No data collected")
    
    big_train_df = pd.concat(all_train_dfs)
    processor.scaler.fit(big_train_df[processor.FEATURE_COLS].values)
    
    # Phase 3: Sequencing & Balancing
    print("--- Phase 3: Sequencing & Balancing ---")
    
    # Helper to get sequences
    def get_sequences(dfs):
        xs, ys = [], []
        for df in dfs:
            feats = df[processor.FEATURE_COLS].values
            scaled = processor.scaler.transform(feats)
            x, y = processor.create_sequences(scaled, df['Target_Class'].values)
            xs.append(x)
            ys.append(y)
        return np.concatenate(xs), np.concatenate(ys)

    x_train_all, y_train_all = get_sequences(all_train_dfs)
    x_val, y_val = get_sequences(all_val_dfs)
    
    # Balancing Logic
    print(f"Raw Train Distribution: {np.bincount(y_train_all)}")
    
    classes = [0, 1, 2]
    class_indices = {c: np.where(y_train_all == c)[0] for c in classes}
    min_count = min([len(idx) for idx in class_indices.values()])
    
    print(f"Balancing to {min_count} samples per class...")
    
    balanced_indices = []
    for c in classes:
        # Randomly sample min_count indices from this class
        balanced_indices.append(np.random.choice(class_indices[c], min_count, replace=False))
        
    final_indices = np.concatenate(balanced_indices)
    np.random.shuffle(final_indices)
    
    x_train = x_train_all[final_indices]
    y_train = y_train_all[final_indices]
    
    print(f"Balanced Train Size: {x_train.shape}")
    
    return x_train, y_train, x_val, y_val, processor

def main():
    import pandas as pd # Needed inside
    
    # Check for existing cache
    if os.path.exists(CACHE_FILE):
        print(f"Loading data from {CACHE_FILE}...")
        try:
            with np.load(CACHE_FILE) as data:
                x_tr = data['x_train']
                y_tr = data['y_train']
                x_v = data['x_val']
                y_v = data['y_val']
            print("Cache loaded successfully.")
            
            # We also need an instance of processor to pass to trainer (for saving scaler paths etc)
            # In a cached run, we assume the scaler at 'brain/saved_models/scaler.pkl' is already good.
            processor = DataProcessor()
            
        except Exception as e:
            print(f"Cache load failed ({e}). Fetching new data...")
            x_tr, y_tr, x_v, y_v, processor = fetch_and_process_correctly()
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            np.savez_compressed(CACHE_FILE, x_train=x_tr, y_train=y_tr, x_val=x_v, y_val=y_v)
    else:
        print("No cache found. Starting fresh fetch...")
        x_tr, y_tr, x_v, y_v, processor = fetch_and_process_correctly()
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        np.savez_compressed(CACHE_FILE, x_train=x_tr, y_train=y_tr, x_val=x_v, y_val=y_v)

    # Shuffle Train
    idx = np.random.permutation(len(x_tr))
    x_tr, y_tr = x_tr[idx], y_tr[idx]

    print(f"Train Size: {x_tr.shape}")
    
    trainer = ModelTrainer()
    # Pass processor so it can save the globally fitted scaler
    trainer.train(processor, x_tr, y_tr, x_v, y_v, epochs=50, learning_rate=0.001)

if __name__ == "__main__":
    main()
