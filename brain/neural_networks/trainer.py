import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import os
import logging
from brain.neural_networks.model import StockLSTM

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model_path="brain/saved_models/hybrid_lstm.pth"):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def train(self, data_processor, x_train, y_train, x_val, y_val, epochs=50, batch_size=64, learning_rate=0.001):
        """
        Classification Training (CrossEntropy) + Accuracy Tracking.
        """
        # Convert targets to LongTensor for CrossEntropy
        train_ds = TensorDataset(torch.FloatTensor(x_train).to(self.device), torch.LongTensor(y_train).to(self.device))
        val_ds = TensorDataset(torch.FloatTensor(x_val).to(self.device), torch.LongTensor(y_val).to(self.device))
        
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
        
        model = StockLSTM(input_size=17).to(self.device)
        criterion = nn.CrossEntropyLoss() 
        optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=5, verbose=True) # Monitor Accuracy (Max)
        
        best_val_acc = 0.0
        patience = 20 
        patience_counter = 0
        
        print(f"Training Classification Model on {self.device}... (Train: {len(x_train)})")
        
        for epoch in range(epochs):
            model.train()
            train_loss_total = 0
            train_correct = 0
            train_total = 0
            
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()
                train_loss_total += loss.item()
                
                # Accuracy Tracking
                _, predicted = torch.max(output.data, 1)
                train_correct += (predicted == batch_y).sum().item()
                train_total += batch_y.size(0)
            
            model.eval()
            val_loss_total = 0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    output = model(batch_x)
                    val_loss = criterion(output, batch_y)
                    val_loss_total += val_loss.item()
                    
                    _, predicted = torch.max(output.data, 1)
                    val_correct += (predicted == batch_y).sum().item()
                    val_total += batch_y.size(0)
            
            # Final Metrics
            avg_train_loss = train_loss_total / len(train_loader)
            avg_val_loss = val_loss_total / len(val_loader)
            
            train_acc = (train_correct / train_total) * 100
            val_acc = (val_correct / val_total) * 100
            
            # Step Scheduler (Monitor Accuracy)
            scheduler.step(val_acc)
            
            # Clean Logging
            print(f"Epoch [{epoch+1:02d}/{epochs}] | "
                  f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
                  f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                torch.save(model.state_dict(), self.model_path)
                data_processor.save_scaler()
            else:
                patience_counter += 1
                
        return model
