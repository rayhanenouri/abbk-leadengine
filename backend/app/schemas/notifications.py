"""
Pydantic schemas for notifications.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.models.models import NotificationType


class NotificationResponse(BaseModel):
    """Notification response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_type: NotificationType
    title: str
    message: str
    lead_id: Optional[int] = None
    extra_data: dict
    is_read: bool
    created_at: datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    user_id: int
    notification_type: NotificationType
    title: str
    message: str
    lead_id: Optional[int] = None
    extra_data: dict = {}


class NotificationMarkRead(BaseModel):
    """Schema for marking notification as read."""
    is_read: bool = True
