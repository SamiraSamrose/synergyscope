# File: backend/agents/visualizer_agent.py
# Purpose: Creates interactive dashboards and graph visualizations


"""
Visualizer Agent (Insight Dashboard & Graph UI)
Creates interactive visualizations using QuickSight and generates graph data
Produces synergy maps, adaptation curves, and patch transition visualizations
"""

import boto3
from typing import Dict, List, Any
import json

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class VisualizerAgent:
    """
    Agent responsible for creating visualization data and dashboards
    Uses AWS QuickSight for advanced analytics dashboards
    """
    
    def __init__(self):
        """Initialize QuickSight and S3 clients"""
        self.quicksight = boto3.client('quicksight', region_name=settings.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        logger.info("Visualizer Agent initialized")
    
    async def create_synergy_visualization(
        self,
        graph_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create synergy network visualization data
        
        Args:
            graph_data: Social graph with nodes and edges
            
        Returns:
            D3.js-compatible graph visualization data
        """
        try:
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            # Format nodes for D3 force graph
            formatted_nodes = []
            for i, node in enumerate(nodes):
                formatted_nodes.append({
                    "id": node['summoner_id'],
                    "name": node['summoner_name'],
                    "group": i % 5,  # Color grouping
                    "value": node.get('wins', 0),
                    "win_rate": node.get('win_rate', 0.0),
                    "radius": 5 + (node.get('wins', 0) / 10)
                })
            
            # Format edges with strength
            formatted_edges = []
            for edge in edges:
                formatted_edges.append({
                    "source": edge['player1_id'],
                    "target": edge['player2_id'],
                    "value": edge.get('synergy_score', 0.0),
                    "co_play_count": edge.get('co_play_count', 0),
                    "strength": edge.get('synergy_score', 0.0) * 10
                })
            
            return {
                "type": "force_directed_graph",
                "nodes": formatted_nodes,
                "links": formatted_edges,
                "config": {
                    "width": 800,
                    "height": 600,
                    "charge": -400,
                    "link_distance": 100
                }
            }
            
        except Exception as e:
            logger.error(f"Synergy visualization creation failed: {e}")
            return {"type": "force_directed_graph", "nodes": [], "links": []}
    
    async def create_adaptation_heatmap(
        self,
        adaptation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create adaptation performance heatmap
        
        Args:
            adaptation_data: Adaptation metrics across patches
            
        Returns:
            Heatmap visualization data
        """
        try:
            metrics = adaptation_data.get('adaptation_metrics', [])
            
            # Create heatmap data
            heatmap_data = []
            for metric in metrics:
                heatmap_data.append({
                    "patch": metric['patch_version'],
                    "win_rate": metric['win_rate'],
                    "games": metric['games_played'],
                    "adaptation_speed": metric['adaptation_speed'],
                    "color_value": metric['win_rate']
                })
            
            return {
                "type": "heatmap",
                "data": heatmap_data,
                "config": {
                    "x_axis": "patch",
                    "y_axis": "metric",
                    "color_scale": ["#ff4444", "#ffaa00", "#00c896"],
                    "min_value": 0.0,
                    "max_value": 1.0
                }
            }
            
        except Exception as e:
            logger.error(f"Adaptation heatmap creation failed: {e}")
            return {"type": "heatmap", "data": []}
    
    async def create_patch_timeline(
        self,
        meta_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create patch evolution timeline
        
        Args:
            meta_data: Meta evolution data across patches
            
        Returns:
            Timeline visualization data
        """
        try:
            patch_data = meta_data.get('patch_data', [])
            
            timeline_data = []
            for patch in patch_data:
                timeline_data.append({
                    "date": patch.get('patch_date', '2024-01-01'),
                    "patch": patch['patch_version'],
                    "win_rate": float(patch.get('win_rate', 0)),
                    "games": int(patch.get('games_played', 0)),
                    "major_changes": patch.get('major_changes', [])
                })
            
            return {
                "type": "timeline",
                "data": timeline_data,
                "config": {
                    "x_axis": "date",
                    "y_axis": "win_rate",
                    "line_color": "#0066cc",
                    "point_size": 6,
                    "show_annotations": True
                }
            }
            
        except Exception as e:
            logger.error(f"Timeline creation failed: {e}")
            return {"type": "timeline", "data": []}
    
    async def create_composition_chart(
        self,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create team composition comparison chart
        
        Args:
            predictions: Composition predictions
            
        Returns:
            Bar chart visualization data
        """
        try:
            compositions = predictions.get('top_compositions', [])
            
            chart_data = []
            for i, comp in enumerate(compositions[:10]):
                chart_data.append({
                    "composition": f"Comp {i+1}",
                    "predicted_win_rate": comp['predicted_win_rate'],
                    "confidence": comp['confidence_score'],
                    "synergy_score": comp.get('meta_alignment', 0.5)
                })
            
            return {
                "type": "bar_chart",
                "data": chart_data,
                "config": {
                    "x_axis": "composition",
                    "y_axis": "predicted_win_rate",
                    "color": "#00c896",
                    "show_values": True
                }
            }
            
        except Exception as e:
            logger.error(f"Composition chart creation failed: {e}")
            return {"type": "bar_chart", "data": []}
    
    async def create_season_recap_visuals(
        self,
        recap_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create comprehensive season recap visualizations
        
        Args:
            recap_data: Season summary data
            
        Returns:
            Multiple visualization configurations
        """
        return {
            "summary_stats": {
                "total_games": recap_data.get('total_games', 0),
                "win_rate": recap_data.get('overall_win_rate', 0.0),
                "best_patch": recap_data.get('peak_performance_patches', [''])[0],
                "adaptation_score": recap_data.get('meta_mastery_score', 0.0)
            },
            "visualizations": [
                {
                    "type": "radial_progress",
                    "title": "Meta Mastery",
                    "value": recap_data.get('meta_mastery_score', 0.0)
                },
                {
                    "type": "teammate_network",
                    "title": "Best Synergies",
                    "data": recap_data.get('best_teammates', [])
                },
                {
                    "type": "growth_curve",
                    "title": "Season Progression",
                    "data": []  # Would include temporal data
                }
            ]
        }
