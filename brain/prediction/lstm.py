import torch
import torch.nn as nn
import torch.nn.functional as F

class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.attention = nn.Linear(hidden_size, 1)

    def forward(self, lstm_output):
        # lstm_output shape: (batch_size, seq_len, hidden_size * 2)
        
        # Calculate attention scores
        # scores shape: (batch_size, seq_len, 1)
        scores = self.attention(lstm_output)
        
        # Normalize scores across time dimension
        weights = F.softmax(scores, dim=1)
        
        # Weighted sum of lstm outputs
        # context shape: (batch_size, hidden_size * 2)
        context = torch.sum(weights * lstm_output, dim=1)
        
        return context, weights

class StockLSTM(nn.Module):
    def __init__(self, input_size=13, hidden_size=64, num_layers=2, dropout=0.2):
        super(StockLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True, 
            dropout=dropout,
            bidirectional=True
        )
        
        # Attention Mechanism
        self.attention = Attention(hidden_size * 2)
        
        # Regularization & Normalization (New additions)
        self.layer_norm = nn.LayerNorm(hidden_size * 2)
        self.dropout = nn.Dropout(0.3)
        
        # Final Output Layer (Raw Logits)
        self.fc = nn.Linear(hidden_size * 2, 1)
        
    def forward(self, x):
        # 1. LSTM Layer
        # Let PyTorch handle h0, c0 initialization (defaults to zeros)
        # out shape: (batch, seq_len, hidden_size * 2)
        out, _ = self.lstm(x)
        
        # 2. Attention Layer
        # context shape: (batch, hidden_size * 2)
        context, _ = self.attention(out)
        
        # 3. Stabilization & Regularization
        context = self.layer_norm(context)
        context = self.dropout(context)
        
        # 4. Final Prediction (Logits)
        # We DO NOT apply sigmoid here. 
        # Use BCEWithLogitsLoss during training.
        # Use torch.sigmoid() during inference.
        logits = self.fc(context)
        
        return logits