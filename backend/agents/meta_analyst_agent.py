# File: backend/agents/meta_analyst_agent.py

"""
Meta Analyst Agent (Meta Tracker)
Tracks patch changes and meta shifts using AWS Glue and Athena
"""

import boto3
import json
from typing import Dict, List, Any
from datetime import datetime

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class MetaAnalystAgent:
    """Tracks meta changes and patch performance"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.athena_client = boto3.client('athena', region_name=settings.AWS_REGION)
        self.bucket = settings.S3_BUCKET
        logger.info("Meta Analyst Agent initialized")
    
    async def get_patch_performance(
        self,
        summoner_id: str,
        season: str = None
    ) -> Dict[str, Any]:
        """Retrieve performance data across patches"""
        try:
            # Mock data for development
            patch_data = self._get_mock_patch_data(summoner_id, season)
            
            meta_impacts = self._calculate_meta_impacts(patch_data)
            
            logger.info(f"Retrieved patch performance for {summoner_id}")
            
            return {
                'summoner_id': summoner_id,
                'patch_data': patch_data,
                'meta_impacts': meta_impacts,
                'total_patches': len(patch_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get patch performance: {e}")
            return {'summoner_id': summoner_id, 'patch_data': [], 'meta_impacts': []}
    
    async def get_current_meta(self, patch_version: str = None) -> Dict[str, Any]:
        """Get current meta state"""
        try:
            if not patch_version:
                patch_version = "14.21"
            
            meta_stats = {
                'top_champions': ['Jinx', 'Caitlyn', 'Thresh', 'Lee Sin', 'Darius'],
                'top_roles': ['BOTTOM', 'UTILITY', 'JUNGLE'],
                'shift_score': 0.65
            }
            
            trends = [
                'ADC carry meta dominance',
                'Tank supports trending upward',
                'Assassin jungle decline'
            ]
            
            return {
                'patch_version': patch_version,
                'meta_state': meta_stats,
                'trends': trends,
                'dominant_champions': meta_stats['top_champions'],
                'dominant_roles': meta_stats['top_roles'],
                'meta_shift_magnitude': meta_stats['shift_score']
            }
            
        except Exception as e:
            logger.error(f"Failed to get current meta: {e}")
            return {'patch_version': patch_version, 'meta_state': {}}
    
    def _get_mock_patch_data(self, summoner_id: str, season: str = None) -> List[Dict]:
        """Return mock patch performance data"""
        patches = ['14.17', '14.18', '14.19', '14.20', '14.21']
        data = []
        
        for i, patch in enumerate(patches):
            games = 20 + (i * 5)
            wins = int(games * (0.48 + (i * 0.03)))
            data.append({
                'patch_version': patch,
                'patch_date': f'2024-{9+i//2:02d}-{(i%2)*15+1:02d}',
                'games_played': games,
                'wins': wins,
                'losses': games - wins,
                'win_rate': wins / games,
                'avg_kda': 2.5 + (i * 0.2),
                'avg_gold': 12000 + (i * 500),
                'avg_damage': 18000 + (i * 1000),
                'major_changes': ['ADC buffs'] if i % 2 == 0 else ['Jungle nerfs'],
                'meta_shift_type': 'moderate' if i < 3 else 'major'
            })
        
        return data
    
    def _calculate_meta_impacts(self, patch_data: List[Dict]) -> List[Dict]:
        """Calculate meta impact scores"""
        impacts = []
        
        for i, patch in enumerate(patch_data):
            if i == 0:
                impact_score = 0.0
            else:
                prev = patch_data[i - 1]
                wr_delta = patch['win_rate'] - prev['win_rate']
                games_delta = patch['games_played'] - prev['games_played']
                impact_score = abs(wr_delta) * 10 + abs(games_delta) / 100
            
            impacts.append({
                'patch_version': patch['patch_version'],
                'impact_score': impact_score,
                'performance_change': 'positive' if impact_score > 0 else 'negative'
            })
        
        return impacts
