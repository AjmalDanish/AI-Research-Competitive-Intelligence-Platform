"""
Pydantic schemas for API validation.
"""

from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
    CompetitorListResponse,
)

from app.schemas.market import (
    MarketIntelligenceCreate,
    MarketIntelligenceUpdate,
    MarketIntelligenceResponse,
    MarketAnalysisResponse,
)

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    TokenResponse,
)

from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
)

from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityListResponse,
)

from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
)

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

from app.schemas.news import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsListResponse,
    NewsSearchResponse,
)

from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearchResponse,
)

from app.schemas.common import (
    MessageResponse,
    HealthResponse,
)

__all__ = [
    # Competitor schemas
    "CompetitorCreate",
    "CompetitorUpdate",
    "CompetitorResponse",
    "CompetitorListResponse",
    
    # Market schemas
    "MarketIntelligenceCreate",
    "MarketIntelligenceUpdate",
    "MarketIntelligenceResponse",
    "MarketAnalysisResponse",
    
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    
    # Alert schemas
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    
    # Activity schemas
    "ActivityCreate",
    "ActivityResponse",
    "ActivityListResponse",
    
    # Report schemas
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportListResponse",
    
    # Product schemas
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    
    # News schemas
    "NewsCreate",
    "NewsUpdate",
    "NewsResponse",
    "NewsListResponse",
    "NewsSearchResponse",
    
    # Search schemas
    "SearchQuery",
    "SearchResponse",
    "SavedSearchCreate",
    "SavedSearchUpdate",
    "SavedSearchResponse",
    
    # Common schemas
    "MessageResponse",
    "HealthResponse",
]