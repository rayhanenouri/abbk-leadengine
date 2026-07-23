"""
Pydantic schemas for user management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.models import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user (Admin only)."""
    email: EmailStr
    full_name: str
    password: str
    role: UserRole
    permissions: Optional[dict] = None


class UserUpdate(BaseModel):
    """Schema for updating a user (Admin only)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    permissions: Optional[dict] = None


class ApproveUserRequest(BaseModel):
    """Schema for approving a pending user."""
    role: UserRole


class UpdateRoleRequest(BaseModel):
    """Schema for updating user role."""
    role: UserRole
