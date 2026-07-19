"""
Search schemas for API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class SearchQuery(BaseModel):
    """Schema for search query."""

    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """Schema for individual search result."""

    id: str
    type: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: List[SearchResultItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class SavedSearchBase(BaseModel):
    """Base saved search schema."""

    name: str = Field(..., min_length=1, max_length=255)
    query: str = Field(..., min_length=1, max_length=2000)
    filters: Optional[Dict[str, Any]] = None


class SavedSearchCreate(SavedSearchBase):
    """Schema for creating a saved search."""

    pass


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    query: Optional[str] = Field(None, min_length=1, max_length=2000)
    filters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SavedSearchInDB(SavedSearchBase):
    """Schema for saved search in database."""

    id: str
    user_id: str
    is_active: bool = True
    last_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedSearchResponse(SavedSearchInDB):
    """Schema for saved search response."""

    pass
