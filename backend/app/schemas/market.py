"""
Market schemas for API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class MarketTrend(BaseModel):
    """Market trend schema."""

    period: str
    value: float
    change_percentage: float


class MarketForecast(BaseModel):
    """Market forecast schema."""

    period: str
    predicted_value: float
    confidence_interval: tuple[float, float]


class MarketIntelligenceBase(BaseModel):
    """Base market intelligence schema."""

    market_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    market_size: Optional[float] = Field(None, ge=0)
    growth_rate: Optional[float] = None


class MarketIntelligenceCreate(MarketIntelligenceBase):
    """Schema for creating market intelligence."""

    pass


class MarketIntelligenceUpdate(BaseModel):
    """Schema for updating market intelligence."""

    market_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    market_size: Optional[float] = Field(None, ge=0)
    growth_rate: Optional[float] = None


class MarketIntelligenceInDB(MarketIntelligenceBase):
    """Schema for market intelligence in database."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketIntelligenceResponse(MarketIntelligenceInDB):
    """Schema for market intelligence response."""

    trends: List[MarketTrend] = []
    forecasts: List[MarketForecast] = []


class MarketAnalysisResponse(BaseModel):
    """Schema for market analysis response."""

    market_share: Dict[str, float]
    growth_trends: List[MarketTrend]
    competitive_landscape: Dict[str, Any]
    opportunities: List[str]
    risks: List[str]
