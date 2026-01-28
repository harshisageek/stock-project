import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import os
from brain.neural_networks.model import StockLSTM

class ModelTrainer:
    def __init__(self, model_path="brain/saved_models/hybrid_lstm.pth"):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def train(self, x_train, y_train, x_val, y_val, epochs=50, batch_size=64, learning_rate=0.001):
        # 1. Create Datasets directly from pre-split data (No random_split!)
        train_ds = TensorDataset(torch.FloatTensor(x_train).to(self.device), torch.FloatTensor(y_train).view(-1, 1).to(self.device))
        val_ds = TensorDataset(torch.FloatTensor(x_val).to(self.device), torch.FloatTensor(y_val).view(-1, 1).to(self.device))
        
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
        
        # 2. Initialize Model
        model = StockLSTM(input_size=13).to(self.device)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4) # Regularization
        
        best_val_loss = float('inf')
        print(f"Training on {self.device}... (Train: {len(x_train)}, Val: {len(x_val)})")
        
        for epoch in range(epochs):
            model.train()
            train_loss = 0
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            model.eval()
            val_loss = 0
            correct = 0
            total = 0
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    outputs = model(batch_x)
                    val_loss += criterion(outputs, batch_y).item()
                    predicted = (outputs > 0.5).float()
                    correct += (predicted == batch_y).sum().item()
                    total += batch_y.size(0)
            
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            val_acc = correct / total
            
            print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.4f}")
            
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                torch.save(model.state_dict(), self.model_path)
                
        print(f"--- Training Complete. Best Val Loss: {best_val_loss:.4f} ---")
        return model
