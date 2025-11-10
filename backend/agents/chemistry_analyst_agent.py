# File: backend/agents/chemistry_analyst_agent.py

"""
Chemistry Analyst Agent (Synergy Quantifier)
Uses Graph Neural Networks to quantify player synergy
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import numpy as np
from typing import Dict, List, Any

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class SynergyGNN(nn.Module):
    """Graph Neural Network for synergy prediction"""
    
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=1):
        super(SynergyGNN, self).__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.conv3(x, edge_index)
        return torch.sigmoid(x)


class ChemistryAnalystAgent:
    """Analyzes player chemistry using GNN models"""
    
    def __init__(self):
        self.model = SynergyGNN()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        logger.info("Chemistry Analyst Agent initialized")
    
    async def analyze_synergies(
        self,
        graph_data: Dict[str, Any],
        patch_version: str = None
    ) -> Dict[str, Any]:
        """Analyze synergies in player graph"""
        try:
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            if not nodes or not edges:
                logger.warning("Empty graph data")
                return self._empty_response()
            
            # Prepare graph tensors
            node_features, edge_index = self._prepare_tensors(nodes, edges)
            
            # Run GNN inference
            synergy_scores = await self._compute_synergy_scores(node_features, edge_index)
            
            # Identify patterns
            strong_pairs = self._identify_strong_pairs(edges, synergy_scores)
            friction_zones = self._identify_friction_zones(edges, synergy_scores)
            
            logger.info(f"Analyzed synergies for {len(nodes)} players")
            
            return {
                'synergy_scores': synergy_scores.tolist(),
                'strong_pairs': strong_pairs,
                'friction_zones': friction_zones,
                'chemistry_ratings': self._calculate_ratings(synergy_scores),
                'average_synergy': float(synergy_scores.mean()),
                'patch_version': patch_version
            }
            
        except Exception as e:
            logger.error(f"Synergy analysis failed: {e}")
            return self._empty_response()
    
    def _prepare_tensors(self, nodes: List[Dict], edges: List[Dict]) -> tuple:
        """Convert graph data to PyTorch tensors"""
        node_features = []
        node_id_map = {}
        
        for idx, node in enumerate(nodes):
            node_id_map[node['summoner_id']] = idx
            features = [
                node.get('win_rate', 0.0),
                node.get('wins', 0) + node.get('losses', 0),
                node.get('wins', 0) / max(1, node.get('wins', 0) + node.get('losses', 0))
            ]
            features.extend([0.0] * (64 - len(features)))
            node_features.append(features)
        
        node_features = torch.tensor(node_features, dtype=torch.float32)
        
        edge_list = []
        for edge in edges:
            src = node_id_map.get(edge.get('player1_id'))
            dst = node_id_map.get(edge.get('player2_id'))
            if src is not None and dst is not None:
                edge_list.append([src, dst])
                edge_list.append([dst, src])
        
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous() if edge_list else torch.empty((2, 0), dtype=torch.long)
        
        return node_features.to(self.device), edge_index.to(self.device)
    
    async def _compute_synergy_scores(self, node_features, edge_index) -> np.ndarray:
        """Compute synergy scores using GNN"""
        try:
            self.model.eval()
            with torch.no_grad():
                output = self.model(node_features, edge_index)
                scores = output.cpu().numpy()
            return scores.flatten()
        except Exception as e:
            logger.error(f"GNN inference failed: {e}")
            return np.zeros(len(node_features))
    
    def _identify_strong_pairs(self, edges: List[Dict], scores: np.ndarray) -> List[Dict]:
        """Identify strong synergy pairs"""
        strong = []
        threshold = 0.7
        for i, edge in enumerate(edges):
            if i < len(scores) and scores[i] > threshold:
                strong.append({
                    'player1_id': edge.get('player1_id'),
                    'player2_id': edge.get('player2_id'),
                    'synergy_score': float(scores[i]),
                    'chemistry_type': 'strong'
                })
        return sorted(strong, key=lambda x: x['synergy_score'], reverse=True)[:10]
    
    def _identify_friction_zones(self, edges: List[Dict], scores: np.ndarray) -> List[Dict]:
        """Identify friction zones"""
        friction = []
        threshold = 0.4
        for i, edge in enumerate(edges):
            if i < len(scores) and scores[i] < threshold:
                friction.append({
                    'player1_id': edge.get('player1_id'),
                    'player2_id': edge.get('player2_id'),
                    'synergy_score': float(scores[i]),
                    'chemistry_type': 'friction'
                })
        return sorted(friction, key=lambda x: x['synergy_score'])[:5]
    
    def _calculate_ratings(self, scores: np.ndarray) -> Dict[str, Any]:
        """Calculate chemistry ratings"""
        mean = scores.mean()
        rating = 'Excellent' if mean > 0.7 else 'Good' if mean > 0.6 else 'Moderate' if mean > 0.5 else 'Needs Improvement'
        return {
            'overall_rating': rating,
            'mean_synergy': float(mean),
            'std_synergy': float(scores.std()),
            'high_synergy_pairs': int((scores > 0.7).sum()),
            'low_synergy_pairs': int((scores < 0.4).sum())
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        """Empty response structure"""
        return {
            'synergy_scores': [],
            'strong_pairs': [],
            'friction_zones': [],
            'chemistry_ratings': {},
            'average_synergy': 0.0
        }
