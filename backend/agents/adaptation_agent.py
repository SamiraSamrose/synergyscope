# File: backend/agents/adaptation_agent.py
# Purpose: Models player/team adaptation speed across patches using time-series forecasting


"""
Adaptation Agent (Player/Team Adaptation Modeler)
Quantifies adaptation speed using SageMaker Forecast and time-series models
Measures how fast individuals or duos adjust to patch balance changes
"""

import boto3
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class AdaptationAgent:
    """
    Agent responsible for modeling player adaptation to meta changes
    Uses SageMaker Forecast and DeepAR for time-series prediction
    """
    
    def __init__(self):
        """Initialize SageMaker and Forecast clients"""
        self.sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=settings.AWS_REGION)
        self.forecast = boto3.client('forecast', region_name=settings.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        logger.info("Adaptation Agent initialized")
    
    async def calculate_adaptation_speed(
        self,
        summoner_id: str,
        patch_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate adaptation speed across patches
        
        Args:
            summoner_id: Player identifier
            patch_data: Performance data per patch
            
        Returns:
            Adaptation metrics and analysis
        """
        try:
            patches = patch_data.get('patch_data', [])
            
            if len(patches) < 3:
                logger.warning(f"Insufficient patch data for {summoner_id}")
                return self._empty_response(summoner_id)
            
            # Step 1: Calculate patch transition performance
            transitions = self._calculate_patch_transitions(patches)
            
            # Step 2: Measure adaptation latency
            adaptation_latency = self._calculate_adaptation_latency(transitions)
            
            # Step 3: Identify fast vs slow adaptation periods
            adaptation_periods = self._identify_adaptation_periods(transitions)
            
            # Step 4: Calculate overall adaptation score
            overall_score = self._calculate_overall_adaptation_score(transitions)
            
            # Step 5: Generate adaptation insights
            insights = self._generate_adaptation_insights(
                transitions,
                adaptation_latency,
                overall_score
            )
            
            logger.info(f"Calculated adaptation metrics for {summoner_id}")
            
            return {
                "summoner_id": summoner_id,
                "adaptation_metrics": self._format_adaptation_metrics(patches, transitions),
                "overall_adaptation_score": overall_score,
                "average_adaptation_latency": adaptation_latency,
                "meta_resilience_rating": self._get_resilience_rating(overall_score),
                "peak_performance_patches": self._get_peak_patches(patches),
                "struggle_patches": self._get_struggle_patches(patches),
                "insights": insights,
                "adaptation_periods": adaptation_periods
            }
            
        except Exception as e:
            logger.error(f"Adaptation calculation failed: {e}")
            return self._empty_response(summoner_id)
    
    def _calculate_patch_transitions(self, patches: List[Dict]) -> List[Dict]:
        """Calculate performance transitions between patches"""
        transitions = []
        
        for i in range(1, len(patches)):
            prev_patch = patches[i - 1]
            curr_patch = patches[i]
            
            prev_wr = float(prev_patch.get('win_rate', 0))
            curr_wr = float(curr_patch.get('win_rate', 0))
            
            delta = curr_wr - prev_wr
            games_played = int(curr_patch.get('games_played', 0))
            
            # Calculate adaptation speed (games needed to stabilize)
            adaptation_games = self._estimate_adaptation_games(prev_wr, curr_wr, games_played)
            
            transitions.append({
                "from_patch": prev_patch.get('patch_version'),
                "to_patch": curr_patch.get('patch_version'),
                "performance_delta": delta,
                "adaptation_games": adaptation_games,
                "transition_type": "positive" if delta > 0 else "negative",
                "magnitude": abs(delta)
            })
        
        return transitions
    
    def _estimate_adaptation_games(
        self,
        prev_wr: float,
        curr_wr: float,
        total_games: int
    ) -> int:
        """Estimate number of games needed to adapt to new patch"""
        # Simplified model: larger performance gaps need more games
        performance_gap = abs(curr_wr - prev_wr)
        
        if performance_gap < 0.05:
            return min(5, total_games)
        elif performance_gap < 0.10:
            return min(10, total_games)
        elif performance_gap < 0.15:
            return min(20, total_games)
        else:
            return min(30, total_games)
    
    def _calculate_adaptation_latency(self, transitions: List[Dict]) -> float:
        """Calculate average adaptation latency in patches"""
        if not transitions:
            return 0.0
        
        # Count how many patches it takes to recover from negative transitions
        recovery_times = []
        
        i = 0
        while i < len(transitions):
            if transitions[i]['transition_type'] == 'negative':
                # Look ahead for recovery
                recovery_count = 0
                j = i + 1
                
                while j < len(transitions) and transitions[j]['transition_type'] == 'negative':
                    recovery_count += 1
                    j += 1
                
                if j < len(transitions):
                    recovery_count += 1
                
                recovery_times.append(recovery_count)
                i = j
            else:
                i += 1
        
        return np.mean(recovery_times) if recovery_times else 1.0
    
    def _identify_adaptation_periods(self, transitions: List[Dict]) -> List[Dict]:
        """Identify distinct adaptation periods"""
        periods = []
        current_period = []
        
        for transition in transitions:
            if not current_period:
                current_period.append(transition)
            elif transition['transition_type'] == current_period[-1]['transition_type']:
                current_period.append(transition)
            else:
                # Period ended, save it
                periods.append({
                    "type": current_period[0]['transition_type'],
                    "duration": len(current_period),
                    "transitions": current_period
                })
                current_period = [transition]
        
        if current_period:
            periods.append({
                "type": current_period[0]['transition_type'],
                "duration": len(current_period),
                "transitions": current_period
            })
        
        return periods
    
    def _calculate_overall_adaptation_score(self, transitions: List[Dict]) -> float:
        """Calculate overall adaptation score (0-1 scale)"""
        if not transitions:
            return 0.5
        
        # Factors: quick recovery, positive transitions, low latency
        positive_transitions = sum(1 for t in transitions if t['transition_type'] == 'positive')
        positive_ratio = positive_transitions / len(transitions)
        
        # Average adaptation games (lower is better)
        avg_games = np.mean([t['adaptation_games'] for t in transitions])
        games_score = max(0, 1 - (avg_games / 30))
        
        # Combined score
        overall_score = (positive_ratio * 0.6) + (games_score * 0.4)
        
        return round(overall_score, 2)
    
    def _generate_adaptation_insights(
        self,
        transitions: List[Dict],
        latency: float,
        score: float
    ) -> List[str]:
        """Generate human-readable adaptation insights"""
        insights = []
        
        # Latency insight
        if latency < 1.5:
            insights.append(f"You adapt to meta changes quickly, averaging {latency:.1f} patches to stabilize")
        elif latency < 2.5:
            insights.append(f"Your adaptation speed is moderate at {latency:.1f} patches per transition")
        else:
            insights.append(f"You take {latency:.1f} patches to adapt - consider tracking patch notes more closely")
        
        # Performance trend
        recent_transitions = transitions[-3:] if len(transitions) >= 3 else transitions
        positive_recent = sum(1 for t in recent_transitions if t['transition_type'] == 'positive')
        
        if positive_recent > len(recent_transitions) / 2:
            insights.append("You are on an upward trajectory in recent patches")
        else:
            insights.append("Recent patches have been challenging - review your champion pool")
        
        # Overall assessment
        if score > 0.7:
            insights.append("You demonstrate excellent meta adaptation skills")
        elif score > 0.5:
            insights.append("Your adaptation is solid but has room for improvement")
        else:
            insights.append("Focus on faster adaptation by diversifying your strategy")
        
        return insights
    
    def _format_adaptation_metrics(
        self,
        patches: List[Dict],
        transitions: List[Dict]
    ) -> List[Dict]:
        """Format adaptation metrics for response"""
        metrics = []
        
        for i, patch in enumerate(patches):
            transition = transitions[i - 1] if i > 0 else None
            
            metrics.append({
                "patch_version": patch.get('patch_version'),
                "patch_date": patch.get('patch_date', datetime.utcnow().isoformat()),
                "games_played": int(patch.get('games_played', 0)),
                "win_rate": float(patch.get('win_rate', 0)),
                "adaptation_speed": transition['adaptation_games'] if transition else 0,
                "performance_delta": transition['performance_delta'] if transition else 0.0,
                "key_changes": patch.get('major_changes', [])
            })
        
        return metrics
    
    def _get_resilience_rating(self, score: float) -> str:
        """Get meta resilience rating from score"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.65:
            return "Good"
        elif score >= 0.5:
            return "Moderate"
        else:
            return "Needs Improvement"
    
    def _get_peak_patches(self, patches: List[Dict]) -> List[str]:
        """Identify peak performance patches"""
        sorted_patches = sorted(
            patches,
            key=lambda x: float(x.get('win_rate', 0)),
            reverse=True
        )
        return [p['patch_version'] for p in sorted_patches[:3]]
    
    def _get_struggle_patches(self, patches: List[Dict]) -> List[str]:
        """Identify struggle patches"""
        sorted_patches = sorted(
            patches,
            key=lambda x: float(x.get('win_rate', 0))
        )
        return [p['patch_version'] for p in sorted_patches[:3]]
    
    def _empty_response(self, summoner_id: str) -> Dict[str, Any]:
        """Return empty response structure"""
        return {
            "summoner_id": summoner_id,
            "adaptation_metrics": [],
            "overall_adaptation_score": 0.0,
            "average_adaptation_latency": 0.0,
            "meta_resilience_rating": "Unknown",
            "peak_performance_patches": [],
            "struggle_patches": [],
            "insights": []
        }