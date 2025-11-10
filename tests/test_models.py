# File: tests/test_models.py

import torch
from backend.models.gnn_models import SynergyGCN

def test_synergy_gcn():
    model = SynergyGCN(input_dim=64, hidden_dim=128)
    x = torch.randn(10, 64)
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)
    output = model(x, edge_index)
    assert output.shape[0] == 10