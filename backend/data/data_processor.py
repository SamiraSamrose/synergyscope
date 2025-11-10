# File: backend/data/data_processor.py
# Purpose: Data processing and transformation utilities

"""
Data Processor
Handles ETL operations, data cleaning, and transformation
Prepares data for agent consumption
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataProcessor:
    """
    Processes raw game data into structured formats for agents
    """
    
    def __init__(self):
        """Initialize data processor"""
        logger.info("Data Processor initialized")
    
    def process_match_history(
        self,
        matches: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Convert match history to DataFrame
        
        Args:
            matches: List of processed match dictionaries
            
        Returns:
            Pandas DataFrame with cleaned match data
        """
        try:
            df = pd.DataFrame(matches)
            
            # Clean and transform data
            if not df.empty:
                df['game_duration_minutes'] = df['game_duration'] / 60
                df['patch'] = df['game_version'].apply(self._extract_patch_version)
                df['timestamp'] = pd.to_datetime(df.get('game_creation', datetime.now()))
            
            logger.info(f"Processed {len(df)} matches")
            return df
            
        except Exception as e:
            logger.error(f"Match history processing failed: {e}")
            return pd.DataFrame()
    
    def calculate_player_statistics(
        self,
        match_df: pd.DataFrame,
        puuid: str
    ) -> Dict[str, Any]:
        """
        Calculate aggregate player statistics
        
        Args:
            match_df: Match history DataFrame
            puuid: Player UUID
            
        Returns:
            Dictionary of player stats
        """
        try:
            player_matches = match_df[match_df['puuid'] == puuid]
            
            if player_matches.empty:
                return {}
            
            total_games = len(player_matches)
            wins = player_matches['win'].sum()
            
            stats = {
                'total_games': total_games,
                'wins': int(wins),
                'losses': total_games - int(wins),
                'win_rate': wins / total_games if total_games > 0 else 0.0,
                'avg_kills': player_matches['kills'].mean(),
                'avg_deaths': player_matches['deaths'].mean(),
                'avg_assists': player_matches['assists'].mean(),
                'avg_kda': self._calculate_kda(player_matches)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Player statistics calculation failed: {e}")
            return {}
    
    def identify_duo_partners(
        self,
        matches: List[Dict[str, Any]],
        target_puuid: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Identify frequent duo partners
        
        Args:
            matches: List of match data
            target_puuid: Target player UUID
            
        Returns:
            Dictionary of partner statistics
        """
        try:
            partners = {}
            
            for match in matches:
                teams = match.get('teams', {})
                
                # Find target player's team
                target_team = None
                for team_id, team_players in teams.items():
                    if any(p['puuid'] == target_puuid for p in team_players):
                        target_team = team_players
                        break
                
                if not target_team:
                    continue
                
                # Record co-players
                match_win = any(p['win'] for p in target_team if p['puuid'] == target_puuid)
                
                for player in target_team:
                    if player['puuid'] != target_puuid:
                        partner_id = player['puuid']
                        
                        if partner_id not in partners:
                            partners[partner_id] = {
                                'co_play_count': 0,
                                'combined_wins': 0,
                                'combined_losses': 0
                            }
                        
                        partners[partner_id]['co_play_count'] += 1
                        if match_win:
                            partners[partner_id]['combined_wins'] += 1
                        else:
                            partners[partner_id]['combined_losses'] += 1
            
            # Calculate win rates
            for partner_id, stats in partners.items():
                total = stats['co_play_count']
                stats['combined_win_rate'] = stats['combined_wins'] / total if total > 0 else 0.0
            
            return partners
            
        except Exception as e:
            logger.error(f"Duo partner identification failed: {e}")
            return {}
    
    def group_by_patch(
        self,
        match_df: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """
        Group matches by patch version
        
        Args:
            match_df: Match history DataFrame
            
        Returns:
            Dictionary mapping patches to DataFrames
        """
        try:
            if 'patch' not in match_df.columns:
                match_df['patch'] = match_df['game_version'].apply(self._extract_patch_version)
            
            grouped = {}
            for patch, group in match_df.groupby('patch'):
                grouped[patch] = group
            
            logger.info(f"Grouped matches into {len(grouped)} patches")
            return grouped
            
        except Exception as e:
            logger.error(f"Patch grouping failed: {e}")
            return {}
    
    def _extract_patch_version(self, game_version: str) -> str:
        """Extract patch version from game version string"""
        try:
            parts = game_version.split('.')
            return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else game_version
        except:
            return "unknown"
    
    def _calculate_kda(self, player_matches: pd.DataFrame) -> float:
        """Calculate KDA ratio"""
        try:
            kills = player_matches['kills'].sum()
            deaths = player_matches['deaths'].sum()
            assists = player_matches['assists'].sum()
            
            return (kills + assists) / deaths if deaths > 0 else kills + assists
        except:
            return 0.0
