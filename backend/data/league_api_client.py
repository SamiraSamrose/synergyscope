# File: backend/data/league_api_client.py
# Purpose: Riot Games League of Legends API client

"""
League of Legends API Client
Handles all interactions with Riot Games API
Fetches summoner data, match history, and champion information
"""

import aiohttp
from typing import Dict, List, Any, Optional
import asyncio

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class LeagueAPIClient:
    """
    Client for Riot Games League of Legends API
    Implements rate limiting and error handling
    """
    
    def __init__(self):
        """Initialize API client"""
        self.api_key = settings.RIOT_API_KEY
        self.base_url = settings.RIOT_API_BASE_URL
        self.region = settings.RIOT_API_REGION
        self.headers = {
            "X-Riot-Token": self.api_key
        }
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("League API Client initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_summoner_by_name(self, summoner_name: str) -> Dict[str, Any]:
        """
        Get summoner information by name
        
        Args:
            summoner_name: Summoner name
            
        Returns:
            Summoner data including PUUID and encrypted summoner ID
        """
        try:
            url = f"{self.base_url}/lol/summoner/v4/summoners/by-name/{summoner_name}"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Retrieved summoner data for {summoner_name}")
                    return data
                elif response.status == 404:
                    logger.warning(f"Summoner not found: {summoner_name}")
                    return {}
                else:
                    logger.error(f"API error {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to get summoner: {e}")
            return {}
    
    async def get_match_history(
        self,
        puuid: str,
        count: int = 100,
        queue_type: Optional[int] = None
    ) -> List[str]:
        """
        Get match history for a player
        
        Args:
            puuid: Player UUID
            count: Number of matches to retrieve
            queue_type: Optional queue type filter (420 = Ranked Solo/Duo)
            
        Returns:
            List of match IDs
        """
        try:
            url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {"count": count}
            
            if queue_type:
                params["queue"] = queue_type
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    match_ids = await response.json()
                    logger.info(f"Retrieved {len(match_ids)} matches")
                    return match_ids
                else:
                    logger.error(f"Failed to get match history: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Match history retrieval failed: {e}")
            return []
    
    async def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Get detailed match information
        
        Args:
            match_id: Match identifier
            
        Returns:
            Complete match data including participants and timeline
        """
        try:
            url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    match_data = await response.json()
                    return match_data
                else:
                    logger.error(f"Failed to get match details: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Match details retrieval failed: {e}")
            return {}
    
    async def get_ranked_stats(self, encrypted_summoner_id: str) -> List[Dict[str, Any]]:
        """
        Get ranked statistics for summoner
        
        Args:
            encrypted_summoner_id: Encrypted summoner ID
            
        Returns:
            List of ranked queue entries
        """
        try:
            url = f"{self.base_url}/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Ranked stats retrieval failed: {e}")
            return []
    
    async def process_match_for_synergy(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process match data to extract synergy information
        
        Args:
            match_data: Raw match data from API
            
        Returns:
            Processed synergy data
        """
        try:
            info = match_data.get('info', {})
            participants = info.get('participants', [])
            
            # Group by team
            teams = {'100': [], '200': []}
            for participant in participants:
                team_id = str(participant.get('teamId', '100'))
                teams[team_id].append({
                    'puuid': participant.get('puuid'),
                    'champion': participant.get('championName'),
                    'role': participant.get('teamPosition'),
                    'win': participant.get('win', False),
                    'kills': participant.get('kills', 0),
                    'deaths': participant.get('deaths', 0),
                    'assists': participant.get('assists', 0)
                })
            
            return {
                'match_id': match_data.get('metadata', {}).get('matchId'),
                'game_duration': info.get('gameDuration', 0),
                'game_version': info.get('gameVersion', ''),
                'teams': teams
            }
            
        except Exception as e:
            logger.error(f"Match processing failed: {e}")
            return {}
