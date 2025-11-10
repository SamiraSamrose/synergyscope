# File: backend/models/recommendation_models.py
# Complete recommendation system models

"""
Recommendation Models
Collaborative filtering and matrix factorization for team composition recommendations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, List

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class MatrixFactorization(nn.Module):
    """
    Matrix Factorization for player-champion recommendations
    """
    
    def __init__(
        self,
        num_players: int,
        num_champions: int,
        embedding_dim: int = 64,
        dropout: float = 0.2
    ):
        super(MatrixFactorization, self).__init__()
        
        # Player embeddings
        self.player_embeddings = nn.Embedding(num_players, embedding_dim)
        self.player_bias = nn.Embedding(num_players, 1)
        
        # Champion embeddings
        self.champion_embeddings = nn.Embedding(num_champions, embedding_dim)
        self.champion_bias = nn.Embedding(num_champions, 1)
        
        # Global bias
        self.global_bias = nn.Parameter(torch.zeros(1))
        
        self.dropout = nn.Dropout(dropout)
        
        # Initialize embeddings
        nn.init.normal_(self.player_embeddings.weight, std=0.01)
        nn.init.normal_(self.champion_embeddings.weight, std=0.01)
        nn.init.zeros_(self.player_bias.weight)
        nn.init.zeros_(self.champion_bias.weight)
    
    def forward(
        self,
        player_ids: torch.Tensor,
        champion_ids: torch.Tensor
    ) -> torch.Tensor:
        """
        Predict affinity score
        
        Args:
            player_ids: Player indices [batch_size]
            champion_ids: Champion indices [batch_size]
            
        Returns:
            Predicted scores [batch_size]
        """
        # Get embeddings
        player_emb = self.player_embeddings(player_ids)
        champion_emb = self.champion_embeddings(champion_ids)
        
        # Apply dropout
        player_emb = self.dropout(player_emb)
        champion_emb = self.dropout(champion_emb)
        
        # Dot product
        interaction = (player_emb * champion_emb).sum(dim=-1)
        
        # Add biases
        player_b = self.player_bias(player_ids).squeeze()
        champion_b = self.champion_bias(champion_ids).squeeze()
        
        prediction = interaction + player_b + champion_b + self.global_bias
        
        return torch.sigmoid(prediction)


class NeuralCollaborativeFiltering(nn.Module):
    """
    Neural Collaborative Filtering (NCF)
    Combines GMF and MLP for recommendations
    """
    
    def __init__(
        self,
        num_players: int,
        num_champions: int,
        embedding_dim: int = 64,
        mlp_layers: List[int] = [128, 64, 32],
        dropout: float = 0.2
    ):
        super(NeuralCollaborativeFiltering, self).__init__()
        
        # GMF embeddings
        self.gmf_player_embedding = nn.Embedding(num_players, embedding_dim)
        self.gmf_champion_embedding = nn.Embedding(num_champions, embedding_dim)
        
        # MLP embeddings
        self.mlp_player_embedding = nn.Embedding(num_players, embedding_dim)
        self.mlp_champion_embedding = nn.Embedding(num_champions, embedding_dim)
        
        # MLP layers
        mlp_modules = []
        input_size = embedding_dim * 2
        for hidden_size in mlp_layers:
            mlp_modules.append(nn.Linear(input_size, hidden_size))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.Dropout(dropout))
            input_size = hidden_size
        
        self.mlp = nn.Sequential(*mlp_modules)
        
        # Final prediction layer
        self.prediction = nn.Linear(embedding_dim + mlp_layers[-1], 1)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        nn.init.normal_(self.gmf_player_embedding.weight, std=0.01)
        nn.init.normal_(self.gmf_champion_embedding.weight, std=0.01)
        nn.init.normal_(self.mlp_player_embedding.weight, std=0.01)
        nn.init.normal_(self.mlp_champion_embedding.weight, std=0.01)
    
    def forward(
        self,
        player_ids: torch.Tensor,
        champion_ids: torch.Tensor
    ) -> torch.Tensor:
        """Forward pass combining GMF and MLP"""
        # GMF part
        gmf_player = self.gmf_player_embedding(player_ids)
        gmf_champion = self.gmf_champion_embedding(champion_ids)
        gmf_output = gmf_player * gmf_champion
        
        # MLP part
        mlp_player = self.mlp_player_embedding(player_ids)
        mlp_champion = self.mlp_champion_embedding(champion_ids)
        mlp_input = torch.cat([mlp_player, mlp_champion], dim=-1)
        mlp_output = self.mlp(mlp_input)
        
        # Concatenate
        concat = torch.cat([gmf_output, mlp_output], dim=-1)
        
        # Prediction
        prediction = self.prediction(concat)
        
        return torch.sigmoid(prediction)


class TeamCompositionRecommender(nn.Module):
    """
    Team composition recommender
    Considers synergies and meta context
    """
    
    def __init__(
        self,
        num_champions: int,
        embedding_dim: int = 64,
        context_dim: int = 32,
        hidden_dim: int = 128
    ):
        super(TeamCompositionRecommender, self).__init__()
        
        # Champion embeddings
        self.champion_embeddings = nn.Embedding(num_champions, embedding_dim)
        
        # Context encoder (meta information)
        self.context_encoder = nn.Sequential(
            nn.Linear(context_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, embedding_dim),
            nn.ReLU()
        )
        
        # Synergy predictor
        self.synergy_predictor = nn.Sequential(
            nn.Linear(embedding_dim * 5 + embedding_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(
        self,
        champion_ids: torch.Tensor,
        meta_context: torch.Tensor
    ) -> torch.Tensor:
        """
        Predict team composition score
        
        Args:
            champion_ids: Champion indices [batch_size, 5] (team of 5)
            meta_context: Meta features [batch_size, context_dim]
            
        Returns:
            Composition scores [batch_size]
        """
        batch_size = champion_ids.size(0)
        
        # Get champion embeddings
        champion_embs = self.champion_embeddings(champion_ids)  # [batch, 5, emb_dim]
        
        # Flatten champion embeddings
        champion_flat = champion_embs.view(batch_size, -1)  # [batch, 5*emb_dim]
        
        # Encode meta context
        context_emb = self.context_encoder(meta_context)  # [batch, emb_dim]
        
        # Concatenate
        combined = torch.cat([champion_flat, context_emb], dim=-1)
        
        # Predict synergy score
        score = self.synergy_predictor(combined)
        
        return torch.sigmoid(score)