"""
Competitor schemas for API responses and requests.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class CompetitorBase(BaseModel):
    """Base competitor schema."""

    name: str = Field(..., min_length=1, max_length=255)
    website: HttpUrl
    industry: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    founded_year: Optional[int] = Field(None, ge=1800, le=2099)
    headquarters: Optional[str] = Field(None, max_length=255)
    market_cap: Optional[float] = Field(None, ge=0)
    employees: Optional[int] = Field(None, ge=0)
    status: str = Field(default="active", pattern="^(active|inactive|acquired)$")


class CompetitorCreate(CompetitorBase):
    """Schema for creating a competitor."""

    pass


class CompetitorUpdate(BaseModel):
    """Schema for updating a competitor."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    founded_year: Optional[int] = Field(None, ge=1800, le=2099)
    headquarters: Optional[str] = Field(None, max_length=255)
    market_cap: Optional[float] = Field(None, ge=0)
    employees: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|acquired)$")


class CompetitorInDB(CompetitorBase):
    """Schema for competitor in database."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompetitorResponse(CompetitorInDB):
    """Schema for competitor response."""

    pass


class CompetitorListResponse(BaseModel):
    """Schema for competitor list response."""

    items: List[CompetitorResponse]
    total: int
    page: int
    page_size: int
