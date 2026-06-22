"""
Pydantic schemas for score history.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.models import ServiceType


class ScoreHistoryResponse(BaseModel):
    """Score history record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    service_type: ServiceType
    service_name: str
    old_score: float
    new_score: float
    change: float
    reason: str | None
    recorded_at: datetime
