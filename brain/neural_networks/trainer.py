import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import os

from brain.neural_networks.model import StockLSTM

class ModelTrainer:
    def __init__(self, model_path="brain/saved_models/hybrid_lstm.pth"):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def train(self, x_train, y_train, epochs=50, batch_size=32, learning_rate=0.001):
        """
        Trains the LSTM model and saves it.
        """
        # Convert to Tensors
        x_tensor = torch.FloatTensor(x_train).to(self.device)
        y_tensor = torch.FloatTensor(y_train).view(-1, 1).to(self.device)
        
        # Create DataLoader
        dataset = TensorDataset(x_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize Model
        # input_size=10 (OHLC, Vol, RSI, MACD, Sig, Sent, News)
        model = StockLSTM(input_size=10).to(self.device)
        
        criterion = nn.BCELoss() # Binary Cross Entropy for Probability
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        print(f"Starting training on {self.device}...")
        
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            total_correct = 0
            total_samples = 0
            
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                # Calculate Accuracy
                predicted = (outputs > 0.5).float()
                total_correct += (predicted == batch_y).sum().item()
                total_samples += batch_y.size(0)
            
            avg_loss = total_loss / len(loader)
            accuracy = total_correct / total_samples
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
                
        # Save Model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(model.state_dict(), self.model_path)
        print(f"Model saved to {self.model_path}")
        
        return model
