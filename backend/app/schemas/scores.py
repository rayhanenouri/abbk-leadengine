"""
Pydantic schemas for scores endpoints.
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.models.models import ServiceType


class ScoreResponse(BaseModel):
    """Individual lead score response."""
    id: int
    lead_id: int
    service_type: ServiceType
    service_name: str
    score: float
    reasoning: str
    signal_breakdown: Dict
    scored_at: datetime

    class Config:
        from_attributes = True


class LeadWithScoresResponse(BaseModel):
    """Lead with all its scores."""
    lead_id: int
    company_name: str
    sector: Optional[str]
    city: Optional[str]
    website: Optional[str]
    scores: List[ScoreResponse]
    best_score: float
    best_service: str


class RankedLeadResponse(BaseModel):
    """Simplified response for ranked leads list."""
    lead_id: int
    company_name: str
    sector: Optional[str]
    city: Optional[str]
    best_score: float
    best_service: str
    best_reasoning: str
