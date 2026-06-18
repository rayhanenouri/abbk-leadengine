"""
Pydantic schemas for leads endpoints.
"""
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional

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
