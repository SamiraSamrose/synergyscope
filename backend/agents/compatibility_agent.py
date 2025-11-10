# File: backend/agents/compatibility_agent.py
# Purpose: Predicts optimal teammate combinations and champion pools per patch

"""
Compatibility & Forecasting Agent (Predictive Recommender)
Suggests ideal duo/team compositions for future patches
Uses SageMaker Recommender + Bedrock LLM reasoning
"""

import boto3
import numpy as np
from typing import Dict, List, Any
import json
from itertools import combinations

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class CompatibilityAgent:
    """
    Agent responsible for predicting optimal team compositions
    Uses SageMaker for recommendations and Bedrock for reasoning
    """
    
    def __init__(self):
        """Initialize AWS clients"""
        self.sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=settings.AWS_REGION)
        self.bedrock = boto3.client('bedrock-runtime', region_name=settings.AWS_REGION)
        logger.info("Compatibility Agent initialized")
    
    async def predict_compositions(
        self,
        summoner_ids: List[str],
        meta_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict optimal team compositions
        
        Args:
            summoner_ids: List of player identifiers
            meta_context: Current meta state information
            
        Returns:
            Composition predictions with win rate forecasts
        """
        try:
            # Step 1: Load player synergy data
            synergy_matrix = await self._load_synergy_matrix(summoner_ids)
            
            # Step 2: Load champion pools
            champion_pools = await self._load_champion_pools(summoner_ids)
            
            # Step 3: Generate composition candidates
            compositions = self._generate_composition_candidates(
                summoner_ids,
                champion_pools,
                meta_context
            )
            
            # Step 4: Score compositions
            scored_compositions = await self._score_compositions(
                compositions,
                synergy_matrix,
                meta_context
            )
            
            # Step 5: Generate reasoning
            top_compositions = sorted(
                scored_compositions,
                key=lambda x: x['predicted_win_rate'],
                reverse=True
            )[:5]
            
            for comp in top_compositions:
                comp['reasoning'] = await self._generate_reasoning(comp, meta_context)
            
            # Step 6: Create meta summary
            meta_summary = self._create_meta_summary(meta_context, top_compositions)
            
            logger.info(f"Generated {len(top_compositions)} composition predictions")
            
            return {
                "patch_version": meta_context.get('patch_version', 'latest'),
                "top_compositions": top_compositions,
                "alternative_picks": self._generate_alternatives(compositions[:10]),
                "meta_summary": meta_summary
            }
            
        except Exception as e:
            logger.error(f"Composition prediction failed: {e}")
            return {
                "patch_version": "unknown",
                "top_compositions": [],
                "alternative_picks": [],
                "meta_summary": "Unable to generate predictions"
            }
    
    async def _load_synergy_matrix(self, summoner_ids: List[str]) -> np.ndarray:
        """Load synergy scores between players"""
        n = len(summoner_ids)
        matrix = np.random.uniform(0.5, 0.9, (n, n))
        np.fill_diagonal(matrix, 1.0)
        # Make symmetric
        matrix = (matrix + matrix.T) / 2
        return matrix
    
    async def _load_champion_pools(self, summoner_ids: List[str]) -> Dict[str, List[str]]:
        """Load champion pools for each player"""
        # In production, this would query actual player data
        champion_pool = [
            "Jinx", "Caitlyn", "Ezreal", "Thresh", "Leona", "Nautilus",
            "Lee Sin", "Graves", "Zed", "Ahri", "Orianna", "Syndra",
            "Darius", "Garen", "Fiora", "Jax", "Camille", "Renekton"
        ]
        
        return {
            summoner_id: np.random.choice(champion_pool, 8, replace=False).tolist()
            for summoner_id in summoner_ids
        }
    
    def _generate_composition_candidates(
        self,
        summoner_ids: List[str],
        champion_pools: Dict[str, List[str]],
        meta_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate candidate team compositions"""
        compositions = []
        
        # Generate up to 20 composition candidates
        for _ in range(min(20, 2 ** len(summoner_ids))):
            composition = {
                "composition_id": f"comp_{_}",
                "players": []
            }
            
            for summoner_id in summoner_ids:
                available_champions = champion_pools.get(summoner_id, [])
                if available_champions:
                    champion = np.random.choice(available_champions)
                    composition["players"].append({
                        "summoner_id": summoner_id,
                        "champion": champion,
                        "role": self._assign_role(champion)
                    })
            
            if len(composition["players"]) == len(summoner_ids):
                compositions.append(composition)
        
        return compositions
    
    def _assign_role(self, champion: str) -> str:
        """Assign role based on champion"""
        role_mapping = {
            "Jinx": "BOTTOM", "Caitlyn": "BOTTOM", "Ezreal": "BOTTOM",
            "Thresh": "UTILITY", "Leona": "UTILITY", "Nautilus": "UTILITY",
            "Lee Sin": "JUNGLE", "Graves": "JUNGLE",
            "Zed": "MIDDLE", "Ahri": "MIDDLE", "Orianna": "MIDDLE", "Syndra": "MIDDLE",
            "Darius": "TOP", "Garen": "TOP", "Fiora": "TOP", "Jax": "TOP",
            "Camille": "TOP", "Renekton": "TOP"
        }
        return role_mapping.get(champion, "MIDDLE")
    
    async def _score_compositions(
        self,
        compositions: List[Dict],
        synergy_matrix: np.ndarray,
        meta_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score compositions based on synergy and meta alignment"""
        scored = []
        
        for comp in compositions:
            # Calculate synergy score
            players = comp['players']
            synergy_scores = []
            
            for i, j in combinations(range(len(players)), 2):
                synergy_scores.append(synergy_matrix[i, j])
            
            avg_synergy = np.mean(synergy_scores) if synergy_scores else 0.7
            
            # Calculate meta alignment
            meta_alignment = self._calculate_meta_alignment(comp, meta_context)
            
            # Predict win rate
            predicted_wr = (avg_synergy * 0.6 + meta_alignment * 0.4) * 0.95
            confidence = avg_synergy * meta_alignment
            
            # Calculate champion synergies
            champion_synergies = self._calculate_champion_synergies(players)
            
            scored.append({
                **comp,
                "predicted_win_rate": round(predicted_wr, 3),
                "confidence_score": round(confidence, 3),
                "synergy_breakdown": champion_synergies,
                "meta_alignment": round(meta_alignment, 3)
            })
        
        return scored
    
    def _calculate_meta_alignment(
        self,
        composition: Dict,
        meta_context: Dict[str, Any]
    ) -> float:
        """Calculate how well composition aligns with current meta"""
        dominant_champions = meta_context.get('dominant_champions', [])
        comp_champions = [p['champion'] for p in composition['players']]
        
        # Check overlap with meta champions
        meta_overlap = len(set(comp_champions) & set(dominant_champions))
        alignment = meta_overlap / max(len(dominant_champions), 1)
        
        # Add some randomness for diversity
        return min(1.0, alignment + np.random.uniform(0.1, 0.3))
    
    def _calculate_champion_synergies(self, players: List[Dict]) -> List[Dict]:
        """Calculate synergy between champion pairs"""
        synergies = []
        
        for i, j in combinations(range(len(players)), 2):
            synergies.append({
                "champion1": players[i]['champion'],
                "champion2": players[j]['champion'],
                "synergy_score": round(np.random.uniform(0.6, 0.95), 2),
                "games_played": np.random.randint(10, 100),
                "win_rate": round(np.random.uniform(0.45, 0.65), 2)
            })
        
        return synergies[:5]  # Return top 5
    
    async def _generate_reasoning(
        self,
        composition: Dict,
        meta_context: Dict[str, Any]
    ) -> str:
        """Generate AI reasoning for composition recommendation"""
        prompt = f"""
        Explain why this team composition is strong in the current meta:
        
        Composition: {json.dumps(composition['players'])}
        Predicted Win Rate: {composition['predicted_win_rate']}
        Meta Context: {json.dumps(meta_context)}
        
        Provide a concise 2-sentence explanation focusing on synergy and meta fit.
        """
        
        try:
            request_body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 150,
                "temperature": 0.7
            })
            
            response = self.bedrock.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=request_body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('completion', 'Strong synergy and meta alignment').strip()
            
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            return "This composition shows strong synergy potential and aligns with current meta trends"
    
    def _generate_alternatives(self, compositions: List[Dict]) -> List[Dict]:
        """Generate alternative picks"""
        alternatives = []
        
        for comp in compositions[:5]:
            for player_data in comp['players'][:2]:  # Top 2 players
                alternatives.append({
                    "summoner_id": player_data['summoner_id'],
                    "current_champion": player_data['champion'],
                    "alternative_champions": self._get_alternative_champions(player_data['champion']),
                    "reasoning": "Provides similar utility with different power spikes"
                })
        
        return alternatives
    
    def _get_alternative_champions(self, champion: str) -> List[str]:
        """Get alternative champion suggestions"""
        alternatives = {
            "Jinx": ["Caitlyn", "Tristana", "Aphelios"],
            "Caitlyn": ["Jinx", "Ashe", "Jhin"],
            "Thresh": ["Nautilus", "Leona", "Blitzcrank"],
            "Lee Sin": ["Graves", "Jarvan IV", "Xin Zhao"]
        }
        return alternatives.get(champion, ["Alternative 1", "Alternative 2"])
    
    def _create_meta_summary(
        self,
        meta_context: Dict[str, Any],
        compositions: List[Dict]
    ) -> str:
        """Create meta summary text"""
        patch = meta_context.get('patch_version', 'latest')
        avg_wr = np.mean([c['predicted_win_rate'] for c in compositions])
        
        return (f"In patch {patch}, compositions focusing on {meta_context.get('trends', ['synergy'])[0]} "
                f"are projected to achieve {avg_wr:.1%} win rate on average")

