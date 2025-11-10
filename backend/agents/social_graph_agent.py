# File: backend/agents/social_graph_agent.py

"""
Social Graph Agent (Graph Builder)
Builds dynamic relationship graphs between players using AWS Neptune
"""

import asyncio
from typing import Dict, List, Any, Optional
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
import boto3

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class SocialGraphAgent:
    """Builds player relationship graphs using AWS Neptune"""
    
    def __init__(self):
        self.endpoint = f"wss://{settings.NEPTUNE_ENDPOINT}:{settings.NEPTUNE_PORT}/gremlin"
        self.client = None
        self._initialize_client()
        logger.info("Social Graph Agent initialized")
    
    def _initialize_client(self):
        """Initialize Neptune Gremlin client"""
        try:
            self.client = client.Client(
                self.endpoint,
                'g',
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
            logger.info("Neptune client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Neptune: {e}")
            # Use mock client for development
            self.client = None
    
    async def create_player_node(self, summoner_id: str, player_data: Dict[str, Any]) -> bool:
        """Create or update player node in graph"""
        try:
            if not self.client:
                logger.warning("Neptune client not available, using mock mode")
                return True
            
            query = """
            g.V().has('summoner', 'id', summoner_id)
                .fold()
                .coalesce(
                    unfold(),
                    addV('summoner').property('id', summoner_id)
                )
                .property('name', name)
                .property('wins', wins)
                .property('losses', losses)
                .property('win_rate', win_rate)
                .property('updated_at', updated_at)
            """
            
            bindings = {
                'summoner_id': summoner_id,
                'name': player_data.get('name', 'Unknown'),
                'wins': player_data.get('wins', 0),
                'losses': player_data.get('losses', 0),
                'win_rate': player_data.get('win_rate', 0.0),
                'updated_at': player_data.get('updated_at', '')
            }
            
            self.client.submit(query, bindings)
            logger.info(f"Created/updated player node: {summoner_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create player node: {e}")
            return False
    
    async def create_synergy_edge(
        self,
        player1_id: str,
        player2_id: str,
        synergy_data: Dict[str, Any]
    ) -> bool:
        """Create synergy edge between two players"""
        try:
            if not self.client:
                return True
            
            query = """
            g.V().has('summoner', 'id', player1_id).as('p1')
                .V().has('summoner', 'id', player2_id).as('p2')
                .coalesce(
                    __.select('p1').outE('plays_with').where(inV().as('p2')),
                    __.select('p1').addE('plays_with').to('p2')
                )
                .property('co_play_count', co_play_count)
                .property('combined_wins', combined_wins)
                .property('combined_win_rate', combined_win_rate)
                .property('synergy_score', synergy_score)
            """
            
            bindings = {
                'player1_id': player1_id,
                'player2_id': player2_id,
                'co_play_count': synergy_data.get('co_play_count', 0),
                'combined_wins': synergy_data.get('combined_wins', 0),
                'combined_win_rate': synergy_data.get('combined_win_rate', 0.0),
                'synergy_score': synergy_data.get('synergy_score', 0.0)
            }
            
            self.client.submit(query, bindings)
            logger.info(f"Created synergy edge: {player1_id} <-> {player2_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create synergy edge: {e}")
            return False
    
    async def get_player_graph(
        self,
        summoner_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """Retrieve player relationship graph"""
        try:
            if not self.client:
                # Return mock data for development
                return self._get_mock_graph_data(summoner_id)
            
            query = """
            g.V().has('summoner', 'id', summoner_id).as('root')
                .repeat(both('plays_with').simplePath()).times(depth)
                .path()
                .by(valueMap(true))
                .toList()
            """
            
            bindings = {'summoner_id': summoner_id, 'depth': depth}
            result = self.client.submit(query, bindings)
            paths = result.all().result()
            
            # Process graph data
            nodes = {}
            edges = []
            
            for path in paths:
                for i, node in enumerate(path):
                    if isinstance(node, dict):
                        node_id = node.get('id', [''])[0]
                        if node_id and node_id not in nodes:
                            nodes[node_id] = {
                                'summoner_id': node_id,
                                'summoner_name': node.get('name', [''])[0],
                                'wins': node.get('wins', [0])[0],
                                'losses': node.get('losses', [0])[0],
                                'win_rate': node.get('win_rate', [0.0])[0]
                            }
            
            logger.info(f"Retrieved graph for {summoner_id}: {len(nodes)} nodes")
            
            return {
                'summoner_id': summoner_id,
                'nodes': list(nodes.values()),
                'edges': edges,
                'generated_at': '2024-11-08T00:00:00Z',
                'meta_context': {}
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve graph: {e}")
            return self._get_mock_graph_data(summoner_id)
    
    def _get_mock_graph_data(self, summoner_id: str) -> Dict[str, Any]:
        """Return mock graph data for development"""
        return {
            'summoner_id': summoner_id,
            'nodes': [
                {'summoner_id': summoner_id, 'summoner_name': 'Player1', 'wins': 150, 'losses': 120, 'win_rate': 0.56},
                {'summoner_id': 'player2', 'summoner_name': 'Player2', 'wins': 180, 'losses': 140, 'win_rate': 0.56},
                {'summoner_id': 'player3', 'summoner_name': 'Player3', 'wins': 160, 'losses': 135, 'win_rate': 0.54},
                {'summoner_id': 'player4', 'summoner_name': 'Player4', 'wins': 145, 'losses': 125, 'win_rate': 0.54},
                {'summoner_id': 'player5', 'summoner_name': 'Player5', 'wins': 170, 'losses': 150, 'win_rate': 0.53}
            ],
            'edges': [
                {'player1_id': summoner_id, 'player2_id': 'player2', 'co_play_count': 45, 'synergy_score': 0.87},
                {'player1_id': summoner_id, 'player2_id': 'player3', 'co_play_count': 32, 'synergy_score': 0.72},
                {'player1_id': summoner_id, 'player2_id': 'player4', 'co_play_count': 28, 'synergy_score': 0.91},
                {'player1_id': 'player2', 'player2_id': 'player3', 'co_play_count': 25, 'synergy_score': 0.68}
            ],
            'generated_at': '2024-11-08T00:00:00Z',
            'meta_context': {}
        }
    
    async def close(self):
        """Close Neptune client"""
        if self.client:
            self.client.close()
            logger.info("Neptune client closed")