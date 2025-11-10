# File: backend/api/models.py

"""
API Data Models
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    TOP = "TOP"
    JUNGLE = "JUNGLE"
    MIDDLE = "MIDDLE"
    BOTTOM = "BOTTOM"
    UTILITY = "UTILITY"


class SummonerAnalysisRequest(BaseModel):
    summoner_name: str = Field(..., min_length=3, max_length=16)
    region: str = Field(default="na1")
    match_count: int = Field(default=100, ge=10, le=1000)
    include_ranked_only: bool = True


class TeamCompositionRequest(BaseModel):
    summoner_ids: List[str] = Field(..., min_items=2, max_items=5)
    patch_version: Optional[str] = None
    meta_context: Optional[Dict[str, Any]] = None


class MetaChatRequest(BaseModel):
    summoner_id: str
    question: str = Field(..., min_length=5, max_length=500)
    context: Optional[Dict[str, Any]] = None


class PlayerNode(BaseModel):
    summoner_id: str
    summoner_name: str
    matches_played: int
    total_wins: int
    win_rate: float
    preferred_roles: List[Role] = []
    champion_pool: List[str] = []


class SynergyEdge(BaseModel):
    player1_id: str
    player2_id: str
    co_play_count: int
    combined_win_rate: float
    synergy_score: float
    chemistry_rating: str
    best_duo_champions: List[Dict[str, str]] = []


class SynergyGraphResponse(BaseModel):
    summoner_id: str
    nodes: List[PlayerNode]
    edges: List[SynergyEdge]
    generated_at: datetime
    meta_context: Dict[str, Any]


class AdaptationMetric(BaseModel):
    patch_version: str
    patch_date: datetime
    games_played: int
    win_rate: float
    adaptation_speed: float
    performance_delta: float
    key_changes: List[str]


class MetaEvolutionResponse(BaseModel):
    summoner_id: str
    adaptation_metrics: List[AdaptationMetric]
    overall_adaptation_score: float
    meta_resilience_rating: str
    peak_performance_patches: List[str]
    struggle_patches: List[str]
    insights: List[str]


class ChampionSynergy(BaseModel):
    champion1: str
    champion2: str
    synergy_score: float
    games_played: int
    win_rate: float


class TeamCompositionPrediction(BaseModel):
    composition_id: str
    players: List[Dict[str, str]]
    predicted_win_rate: float
    confidence_score: float
    synergy_breakdown: List[ChampionSynergy]
    reasoning: str
    meta_alignment: float


class PredictionsResponse(BaseModel):
    patch_version: str
    top_compositions: List[TeamCompositionPrediction]
    alternative_picks: List[Dict[str, Any]]
    meta_summary: str


class NarrativeInsight(BaseModel):
    insight_type: str
    title: str
    narrative: str
    supporting_data: Dict[str, Any]
    confidence: float
    timestamp: datetime


class SeasonRecapResponse(BaseModel):
    summoner_id: str
    season: str
    total_games: int
    overall_win_rate: float
    best_teammates: List[Dict[str, Any]]
    adaptation_journey: str
    meta_mastery_score: float
    growth_highlights: List[str]
    key_insights: List[NarrativeInsight]
    visualizations: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
