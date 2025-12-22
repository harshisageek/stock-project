import argparse
from brain.neural_networks.data_processor import DataProcessor
from brain.neural_networks.trainer import ModelTrainer
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='Train Hybrid LSTM Stock Predictor')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Ticker to train on')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    args = parser.parse_args()
    
    ticker = args.ticker
    print(f"--- Starting Training Pipeline for {ticker} ---")
    
    # 1. Prepare Data
    print("Step 1: Fetching and Processing Data...")
    processor = DataProcessor(sequence_length=60)
    x_train, y_train = processor.prepare_data(ticker)
    
    if x_train is None:
        print("Error: Could not fetch data or insufficient data.")
        return
        
    print(f"Data Prepared. Training Samples: {len(x_train)}")
    print(f"Features Shape: {x_train.shape}")
    
    # 2. Train Model
    print("Step 2: Initialize Trainer...")
    trainer = ModelTrainer()
    
    print("Step 3: Training Brain...")
    trainer.train(x_train, y_train, epochs=args.epochs)
    
    print("--- Training Complete ---")
    print("Model saved to brain/saved_models/hybrid_lstm.pth")

if __name__ == "__main__":
    main()
