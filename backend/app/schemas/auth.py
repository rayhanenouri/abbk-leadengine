"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.models import UserRole


class LoginRequest(BaseModel):
    """Request body for login endpoint."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Response for successful login."""
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    """Request body for user self-registration."""
    email: EmailStr
    full_name: str
    password: str
    company_role: str | None = None  # Optional field for user's company/position


class UserResponse(BaseModel):
    """User data returned in responses (excludes password)."""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    permissions: dict
    created_at: datetime

    class Config:
        from_attributes = True  # Enables SQLAlchemy model conversion
