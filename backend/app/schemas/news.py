"""
News schemas for API responses and requests.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class NewsBase(BaseModel):
    """Base news schema."""

    title: str = Field(..., min_length=1, max_length=500)
    summary: str = Field(..., max_length=2000)
    source: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    sentiment: str = Field(default="neutral", pattern="^(positive|negative|neutral)$")
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    published_date: Optional[datetime] = None


class NewsCreate(NewsBase):
    """Schema for creating news."""

    pass


class NewsUpdate(BaseModel):
    """Schema for updating news."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[HttpUrl] = None
    sentiment: Optional[str] = Field(None, pattern="^(positive|negative|neutral)$")
    relevance_score: Optional[float] = Field(None, ge=0, le=1)


class NewsInDB(NewsBase):
    """Schema for news in database."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsResponse(NewsInDB):
    """Schema for news response."""

    pass


class NewsListResponse(BaseModel):
    """Schema for news list response."""

    items: List[NewsResponse]
    total: int
    page: int
    page_size: int


class NewsSearchResponse(BaseModel):
    """Schema for news search response."""

    query: str
    results: List[NewsResponse]
    total: int
