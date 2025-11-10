# File: backend/models/time_series_models.py
# Complete time-series forecasting models

"""
Time Series Forecasting Models
Models for adaptation speed prediction and performance forecasting
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class LSTMForecaster(nn.Module):
    """
    LSTM-based time series forecaster
    Predicts future performance based on historical data
    """
    
    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2
    ):
        super(LSTMForecaster, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass
        
        Args:
            x: Input sequence [batch_size, seq_len, input_size]
            hidden: Hidden state tuple (h0, c0)
            
        Returns:
            predictions: Output predictions [batch_size, output_size]
            hidden: Updated hidden state
        """
        # LSTM forward
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Take last time step
        last_output = lstm_out[:, -1, :]
        
        # Prediction layers
        out = self.fc1(last_output)
        out = torch.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out, hidden
    
    def init_hidden(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Initialize hidden state"""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)


class GRUForecaster(nn.Module):
    """
    GRU-based time series forecaster
    Alternative to LSTM with fewer parameters
    """
    
    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2
    ):
        super(GRUForecaster, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # GRU layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Prediction layers
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        hidden: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        gru_out, hidden = self.gru(x, hidden)
        last_output = gru_out[:, -1, :]
        out = self.dropout(last_output)
        out = self.fc(out)
        return out, hidden


class TransformerForecaster(nn.Module):
    """
    Transformer-based time series forecaster
    Uses attention mechanism for long-range dependencies
    """
    
    def __init__(
        self,
        input_size: int = 1,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 3,
        output_size: int = 1,
        dropout: float = 0.2
    ):
        super(TransformerForecaster, self).__init__()
        
        self.d_model = d_model
        
        # Input embedding
        self.embedding = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output layer
        self.fc = nn.Linear(d_model, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Embedding
        x = self.embedding(x) * np.sqrt(self.d_model)
        x = self.pos_encoder(x)
        
        # Transformer encoding
        x = self.transformer_encoder(x)
        
        # Take last time step
        x = x[:, -1, :]
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding"""
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class AdaptationSpeedPredictor(nn.Module):
    """
    Specialized model for adaptation speed prediction
    Combines temporal and structural features
    """
    
    def __init__(
        self,
        temporal_input_size: int = 10,
        structural_input_size: int = 20,
        hidden_size: int = 64,
        output_size: int = 1
    ):
        super(AdaptationSpeedPredictor, self).__init__()
        
        # Temporal feature extractor (LSTM)
        self.lstm = nn.LSTM(
            input_size=temporal_input_size,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True
        )
        
        # Structural feature extractor (MLP)
        self.structural_mlp = nn.Sequential(
            nn.Linear(structural_input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU()
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(
        self,
        temporal_features: torch.Tensor,
        structural_features: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward pass combining temporal and structural features
        
        Args:
            temporal_features: Time series features [batch, seq_len, temporal_input_size]
            structural_features: Graph features [batch, structural_input_size]
            
        Returns:
            Adaptation speed predictions
        """
        # Extract temporal features
        lstm_out, _ = self.lstm(temporal_features)
        temporal_emb = lstm_out[:, -1, :]
        
        # Extract structural features
        structural_emb = self.structural_mlp(structural_features)
        
        # Fuse features
        combined = torch.cat([temporal_emb, structural_emb], dim=-1)
        output = self.fusion(combined)
        
        return output
