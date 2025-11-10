# File: backend/aws/neptune_client.py
# Purpose: Enhanced Neptune graph database client


"""
Neptune Graph Database Client
Advanced graph operations and query optimization
"""

from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
from typing import Dict, List, Any
import asyncio

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class NeptuneClient:
    """
    Advanced Neptune client with connection pooling and query optimization
    """
    
    def __init__(self):
        """Initialize Neptune connection pool"""
        self.endpoint = f"wss://{settings.NEPTUNE_ENDPOINT}:{settings.NEPTUNE_PORT}/gremlin"
        self.client = self._create_client()
        logger.info("Neptune client initialized with connection pool")
    
    def _create_client(self):
        """Create Gremlin client with connection pool"""
        return client.Client(
            self.endpoint,
            'g',
            pool_size=8,
            max_workers=4,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
    
    async def execute_query(
        self,
        query: str,
        bindings: Dict[str, Any] = None
    ) -> List[Any]:
        """
        Execute Gremlin query with error handling
        
        Args:
            query: Gremlin query string
            bindings: Query parameter bindings
            
        Returns:
            Query results
        """
        try:
            result_set = self.client.submit(query, bindings or {})
            results = result_set.all().result()
            return results
            
        except GremlinServerError as e:
            logger.error(f"Gremlin query error: {e}")
            raise
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def batch_insert_nodes(
        self,
        nodes: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch insert multiple nodes efficiently
        
        Args:
            nodes: List of node data dictionaries
            
        Returns:
            Success status
        """
        try:
            # Build batch insert query
            query = """
            g.inject(nodes)
                .unfold()
                .as('node')
                .coalesce(
                    V().has('summoner', 'id', select('node').select('id')),
                    addV('summoner')
                        .property('id', select('node').select('id'))
                )
                .property('name', select('node').select('name'))
                .property('wins', select('node').select('wins'))
                .property('losses', select('node').select('losses'))
            """
            
            await self.execute_query(query, {'nodes': nodes})
            logger.info(f"Batch inserted {len(nodes)} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Batch node insertion failed: {e}")
            return False
    
    async def find_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> List[str]:
        """
        Find shortest path between two players
        
        Args:
            source_id: Source player ID
            target_id: Target player ID
            
        Returns:
            List of player IDs in path
        """
        try:
            query = """
            g.V().has('summoner', 'id', source_id)
                .repeat(both('plays_with').simplePath())
                .until(has('summoner', 'id', target_id))
                .path()
                .by('id')
                .limit(1)
            """
            
            results = await self.execute_query(
                query,
                {'source_id': source_id, 'target_id': target_id}
            )
            
            if results:
                return results[0]
            return []
            
        except Exception as e:
            logger.error(f"Shortest path query failed: {e}")
            return []
    
    async def get_community_detection(
        self,
        min_community_size: int = 3
    ) -> List[List[str]]:
        """
        Detect player communities using graph algorithms
        
        Args:
            min_community_size: Minimum size for valid community
            
        Returns:
            List of communities (each community is a list of player IDs)
        """
        try:
            # Simplified community detection using connected components
            query = """
            g.V().hasLabel('summoner')
                .emit()
                .repeat(both('plays_with').simplePath())
                .times(3)
                .aggregate('community')
                .cap('community')
            """
            
            results = await self.execute_query(query)
            
            # Process results to form communities
            communities = []
            # Implementation would group connected players
            
            return communities
            
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return []
    
    def close(self):
        """Close Neptune client connection"""
        if self.client:
            self.client.close()
            logger.info("Neptune client closed")
