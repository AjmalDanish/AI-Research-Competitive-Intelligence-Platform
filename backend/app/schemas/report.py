"""
Report schemas for API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReportBase(BaseModel):
    """Base report schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    report_type: str = Field(..., pattern="^(competitor|market|analytics|custom)$")
    format: str = Field(..., pattern="^(pdf|excel|csv)$")
    date_range: str = Field(default="30d")


class ReportCreate(ReportBase):
    """Schema for creating a report."""

    pass


class ReportUpdate(BaseModel):
    """Schema for updating a report."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    report_type: Optional[str] = Field(None, pattern="^(competitor|market|analytics|custom)$")
    format: Optional[str] = Field(None, pattern="^(pdf|excel|csv)$")
    status: Optional[str] = Field(None, pattern="^(generating|ready|failed)$")


class ReportInDB(ReportBase):
    """Schema for report in database."""

    id: str
    user_id: str
    status: str = "generating"
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportResponse(ReportInDB):
    """Schema for report response."""

    pass


class ReportListResponse(BaseModel):
    """Schema for report list response."""

    items: List[ReportResponse]
    total: int
    page: int
    page_size: int
