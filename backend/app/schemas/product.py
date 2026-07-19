"""
Product schemas for API responses and requests.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(..., min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    website: Optional[HttpUrl] = None


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    website: Optional[HttpUrl] = None


class ProductInDB(ProductBase):
    """Schema for product in database."""

    id: str
    competitor_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductResponse(ProductInDB):
    """Schema for product response."""

    pass


class ProductListResponse(BaseModel):
    """Schema for product list response."""

    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
