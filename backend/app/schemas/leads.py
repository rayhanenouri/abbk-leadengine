"""
Pydantic schemas for leads endpoints.
"""
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List, Any

from app.models.models import LeadStatus


class LeadBase(BaseModel):
    """Base lead schema with common fields."""
    company_name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    sector: Optional[str] = None
    employee_count: Optional[int] = None


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    pass


class LeadResponse(LeadBase):
    """Lead data returned in responses."""
    id: int
    is_multinational: bool
    is_exporter: bool
    under_audit: bool
    scraped_data: dict
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CSVImportResponse(BaseModel):
    """Response for CSV import endpoint."""
    imported: int
    skipped: int
    total: int
    message: str


class LeadWithSignalsResponse(BaseModel):
    """Lead with signals and scores included."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    sector: Optional[str] = None
    employee_count: Optional[int] = None
    is_multinational: bool
    is_exporter: bool
    under_audit: bool
    scraped_data: dict
    status: LeadStatus
    created_at: datetime
    updated_at: datetime
    signals: Optional[List[Any]] = None  # LeadSignal objects
    scores: Optional[List[Any]] = None   # LeadScore objects


class PaginatedLeadsResponse(BaseModel):
    """Paginated response for GET /api/leads endpoint."""
    leads: List[Any]  # Can be LeadResponse or LeadWithSignalsResponse
    total: int
    skip: int
    limit: int
    has_more: bool
