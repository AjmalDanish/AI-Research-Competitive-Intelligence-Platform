"""
Activity schemas for API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class ActivityBase(BaseModel):
    """Base activity schema."""
    activity_type: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., max_length=500)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=100)


class ActivityCreate(ActivityBase):
    """Schema for creating an activity."""
    pass


class ActivityInDB(ActivityBase):
    """Schema for activity in database."""
    id: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityResponse(ActivityInDB):
    """Schema for activity response."""
    pass


class ActivityListResponse(BaseModel):
    """Schema for activity list response."""
    items: List[ActivityResponse]
    total: int
    page: int
    page_size: int