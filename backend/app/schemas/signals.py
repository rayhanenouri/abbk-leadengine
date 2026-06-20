"""
Pydantic schemas for signals API.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SignalResponse(BaseModel):
    """Response schema for a single signal."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    signal_type: str
    title: str
    detail: str | None = None
    source_url: str | None = None
    detected_at: datetime
