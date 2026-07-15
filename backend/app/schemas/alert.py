"""
Alert schemas for API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AlertBase(BaseModel):
    """Base alert schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=2000)
    alert_type: str = Field(..., pattern="^(competitor|market|pricing|product|news)$")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    status: str = Field(default="active", pattern="^(active|triggered|resolved)$")


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    alert_type: Optional[str] = Field(None, pattern="^(competitor|market|pricing|product|news)$")
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(active|triggered|resolved)$")
    is_read: Optional[bool] = None


class AlertInDB(AlertBase):
    """Schema for alert in database."""
    id: str
    user_id: str
    is_read: bool = False
    triggered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(AlertInDB):
    """Schema for alert response."""
    pass


class AlertListResponse(BaseModel):
    """Schema for alert list response."""
    items: List[AlertResponse]
    total: int
    unread_count: int