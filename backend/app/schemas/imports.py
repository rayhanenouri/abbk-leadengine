"""
Pydantic schemas for database imports.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.models import ImportStatus


# ─── Import Responses ─────────────────────────────────────────────────────────

class ImportCreateResponse(BaseModel):
    """Response after uploading import file."""
    import_id: int
    filename: str
    total_rows: int
    status: ImportStatus
    message: str


class ImportStatusResponse(BaseModel):
    """Import processing status."""
    id: int
    filename: str
    status: ImportStatus
    total_rows: int
    imported_count: int
    duplicates_count: int
    updated_count: int
    errors_count: int
    enriched_count: int
    signals_count: int
    error_details: dict
    created_at: datetime
    completed_at: datetime | None

    # Progress percentage (0-100)
    progress: int = Field(default=0)

    class Config:
        from_attributes = True


class ImportHistoryItem(BaseModel):
    """Single import in history list."""
    id: int
    filename: str
    status: ImportStatus
    total_rows: int
    imported_count: int
    duplicates_count: int
    updated_count: int
    enriched_count: int
    signals_count: int
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


# ─── Import Requests ──────────────────────────────────────────────────────────

class ColumnMappingRequest(BaseModel):
    """Column mapping from user's CSV to our database fields."""
    company_name: str | None = None
    website: str | None = None
    linkedin_url: str | None = None
    country: str | None = None
    city: str | None = None
    sector: str | None = None
    phone: str | None = None
    email: str | None = None
    employee_count: str | None = None
