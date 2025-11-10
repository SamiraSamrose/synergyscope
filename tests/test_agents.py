# File: tests/test_agents.py

import pytest
from backend.agents.social_graph_agent import SocialGraphAgent

@pytest.mark.asyncio
async def test_social_graph_agent():
    agent = SocialGraphAgent()
    result = await agent.get_player_graph("test_player", depth=1)
    assert "nodes" in result
    assert "edges" in result