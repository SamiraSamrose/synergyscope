# File: backend/models/gnn_models.py
# Complete Graph Neural Network model implementations

"""
Graph Neural Network Models
PyTorch implementations for synergy prediction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, SAGEConv, global_mean_pool, global_max_pool
from torch_geometric.data import Data, Batch
from typing import Optional

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class SynergyGCN(nn.Module):
    """
    Graph Convolutional Network for synergy prediction
    Uses multiple GCN layers with residual connections
    """
    
    def __init__(
        self,
        input_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 1,
        num_layers: int = 3,
        dropout: float = 0.3
    ):
        super(SynergyGCN, self).__init__()
        
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Input layer
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        
        # Hidden layers
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        for _ in range(num_layers - 2):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
            self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # Output layer
        self.conv_out = GCNConv(hidden_dim, hidden_dim)
        self.bn_out = nn.BatchNorm1d(hidden_dim)
        
        # Final prediction layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Node features [num_nodes, input_dim]
            edge_index: Edge indices [2, num_edges]
            batch: Batch assignment [num_nodes]
            
        Returns:
            Predictions [batch_size, output_dim] or [num_nodes, output_dim]
        """
        # First layer
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.dropout_layer(x)
        
        # Hidden layers with residual connections
        for conv, bn in zip(self.convs, self.bns):
            x_residual = x
            x = conv(x, edge_index)
            x = bn(x)
            x = F.relu(x)
            x = self.dropout_layer(x)
            x = x + x_residual  # Residual connection
        
        # Output layer
        x = self.conv_out(x, edge_index)
        x = self.bn_out(x)
        x = F.relu(x)
        
        # Global pooling if batch is provided
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        # Final prediction
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout_layer(x)
        x = self.fc2(x)
        
        return torch.sigmoid(x)


class SynergyGAT(nn.Module):
    """
    Graph Attention Network for synergy prediction
    Uses attention mechanisms to weight neighbor importance
    """
    
    def __init__(
        self,
        input_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 1,
        num_heads: int = 4,
        dropout: float = 0.3
    ):
        super(SynergyGAT, self).__init__()
        
        self.dropout = dropout
        
        # GAT layers with multi-head attention
        self.conv1 = GATConv(input_dim, hidden_dim, heads=num_heads, dropout=dropout)
        self.conv2 = GATConv(hidden_dim * num_heads, hidden_dim, heads=num_heads, dropout=dropout)
        self.conv3 = GATConv(hidden_dim * num_heads, hidden_dim, heads=1, concat=False, dropout=dropout)
        
        # Prediction layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with attention"""
        # Layer 1
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = self.dropout_layer(x)
        
        # Layer 2
        x = self.conv2(x, edge_index)
        x = F.elu(x)
        x = self.dropout_layer(x)
        
        # Layer 3
        x = self.conv3(x, edge_index)
        x = F.elu(x)
        
        # Global pooling
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        # Prediction
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout_layer(x)
        x = self.fc2(x)
        
        return torch.sigmoid(x)


class SynergySAGE(nn.Module):
    """
    GraphSAGE for synergy prediction
    Uses sampling and aggregation for scalability
    """
    
    def __init__(
        self,
        input_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 1,
        num_layers: int = 3,
        dropout: float = 0.3,
        aggregator: str = 'mean'
    ):
        super(SynergySAGE, self).__init__()
        
        self.num_layers = num_layers
        self.dropout = dropout
        
        # SAGE layers
        self.convs = nn.ModuleList()
        self.convs.append(SAGEConv(input_dim, hidden_dim, aggr=aggregator))
        
        for _ in range(num_layers - 1):
            self.convs.append(SAGEConv(hidden_dim, hidden_dim, aggr=aggregator))
        
        # Batch normalization
        self.bns = nn.ModuleList([nn.BatchNorm1d(hidden_dim) for _ in range(num_layers)])
        
        # Prediction layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with sampling"""
        for i, (conv, bn) in enumerate(zip(self.convs, self.bns)):
            x = conv(x, edge_index)
            x = bn(x)
            x = F.relu(x)
            if i < len(self.convs) - 1:
                x = self.dropout_layer(x)
        
        # Global pooling
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        # Prediction
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout_layer(x)
        x = self.fc2(x)
        
        return torch.sigmoid(x)


class EdgePredictor(nn.Module):
    """
    Edge prediction module
    Predicts synergy scores for player pairs
    """
    
    def __init__(self, hidden_dim: int = 128):
        super(EdgePredictor, self).__init__()
        
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)
        
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, z_i: torch.Tensor, z_j: torch.Tensor) -> torch.Tensor:
        """
        Predict edge score between nodes
        
        Args:
            z_i: Embeddings of source nodes
            z_j: Embeddings of target nodes
            
        Returns:
            Edge scores
        """
        # Concatenate node embeddings
        x = torch.cat([z_i, z_j], dim=-1)
        
        # MLP
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.fc2(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.fc3(x)
        
        return torch.sigmoid(x)
