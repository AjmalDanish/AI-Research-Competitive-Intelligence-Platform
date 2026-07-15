"""
Common schemas used across multiple endpoints.
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    model_config = ConfigDict(extra="forbid")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T] = Field(default_factory=list, description="List of items")
    total: int = Field(default=0, description="Total number of items")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Items per page")
    total_pages: int = Field(default=0, description="Total number of pages")
    has_next: bool = Field(default=False, description="Whether there is a next page")
    has_previous: bool = Field(default=False, description="Whether there is a previous page")
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether the operation was successful")
    data: Optional[Any] = Field(default=None, description="Additional data")
    
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy", description="Health status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Application environment")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    services: dict = Field(default_factory=dict, description="Service health statuses")
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class ValidationErrorResponse(ErrorResponse):
    """Validation error response."""
    
    errors: List[dict] = Field(default_factory=list, description="Validation errors")
    
    model_config = ConfigDict(from_attributes=True)


class IdResponse(BaseModel):
    """Response with ID."""
    
    id: int = Field(..., description="Resource ID")
    
    model_config = ConfigDict(from_attributes=True)


class BulkDeleteResponse(BaseModel):
    """Response for bulk delete operations."""
    
    deleted_count: int = Field(..., description="Number of items deleted")
    success: bool = Field(default=True, description="Whether the operation was successful")
    
    model_config = ConfigDict(from_attributes=True)


class SearchParams(BaseModel):
    """Search parameters for filtered queries."""
    
    query: Optional[str] = Field(default=None, description="Search query")
    filters: dict = Field(default_factory=dict, description="Filter criteria")
    date_range: Optional[dict] = Field(default=None, description="Date range filter")
    sort: Optional[dict] = Field(default=None, description="Sort configuration")
    
    model_config = ConfigDict(extra="forbid")


class ExportParams(BaseModel):
    """Export parameters for data export."""
    
    format: str = Field(default="json", pattern="^(json|csv|excel|pdf)$", description="Export format")
    include_fields: Optional[List[str]] = Field(default=None, description="Fields to include")
    exclude_fields: Optional[List[str]] = Field(default=None, description="Fields to exclude")
    date_range: Optional[dict] = Field(default=None, description="Date range filter")
    filters: dict = Field(default_factory=dict, description="Additional filters")
    
    model_config = ConfigDict(extra="forbid")


class BulkCreateParams(BaseModel):
    """Parameters for bulk create operations."""
    
    items: List[Any] = Field(..., description="Items to create")
    skip_duplicates: bool = Field(default=False, description="Skip duplicate items")
    update_existing: bool = Field(default=False, description="Update existing items")
    
    model_config = ConfigDict(extra="forbid")


class BulkUpdateParams(BaseModel):
    """Parameters for bulk update operations."""
    
    ids: List[int] = Field(..., description="IDs of items to update")
    updates: dict = Field(..., description="Update data")
    skip_validation: bool = Field(default=False, description="Skip validation")
    
    model_config = ConfigDict(extra="forbid")