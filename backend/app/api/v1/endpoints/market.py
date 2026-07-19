"""
Market intelligence endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional

from app.db.session import get_db
from app.models.market import MarketTrend, MarketIntelligence
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/trends")
async def list_trends(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List market trends with filtering and pagination.
    """
    query = select(MarketTrend)

    if industry:
        query = query.where(MarketTrend.industry == industry)

    if status:
        query = query.where(MarketTrend.status == status)

    query = query.order_by(MarketTrend.detected_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    trends = result.scalars().all()

    return {
        "trends": [
            {
                "id": trend.id,
                "name": trend.name,
                "description": trend.description,
                "category": trend.category,
                "industry": trend.industry,
                "growth_rate": trend.growth_rate,
                "trend_direction": trend.trend_direction,
                "confidence_level": trend.confidence_level,
                "status": trend.status,
                "detected_date": trend.detected_date,
            }
            for trend in trends
        ],
        "total": len(trends),
        "skip": skip,
        "limit": limit,
    }


@router.get("/intelligence")
async def list_intelligence(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List market intelligence with filtering and pagination.
    """
    query = select(MarketIntelligence)

    if industry:
        query = query.where(MarketIntelligence.industry == industry)

    if category:
        query = query.where(MarketIntelligence.category == category)

    query = query.order_by(MarketIntelligence.collected_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    intelligence_items = result.scalars().all()

    return {
        "intelligence": [
            {
                "id": intel.id,
                "title": intel.title,
                "summary": intel.summary,
                "category": intel.category,
                "industry": intel.industry,
                "topic": intel.topic,
                "source_type": intel.source_type,
                "source_name": intel.source_name,
                "sentiment": intel.sentiment,
                "importance_level": intel.importance_level,
                "collected_date": intel.collected_date,
            }
            for intel in intelligence_items
        ],
        "total": len(intelligence_items),
        "skip": skip,
        "limit": limit,
    }


@router.post("/trends", status_code=status.HTTP_201_CREATED)
async def create_trend(
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    industry: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new market trend.
    """
    trend = MarketTrend(
        name=name,
        description=description,
        category=category,
        industry=industry,
        status="active",
    )

    db.add(trend)
    await db.commit()
    await db.refresh(trend)

    logger.info(f"New trend created: {trend.name}")

    return {
        "id": trend.id,
        "message": "Trend created successfully",
    }


@router.get("/trends/{trend_id}")
async def get_trend(trend_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get trend by ID with full details.
    """
    result = await db.execute(select(MarketTrend).where(MarketTrend.id == trend_id))
    trend = result.scalar_one_or_none()

    if not trend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trend not found")

    return {
        "id": trend.id,
        "name": trend.name,
        "description": trend.description,
        "category": trend.category,
        "industry": trend.industry,
        "sector": trend.sector,
        "market_segment": trend.market_segment,
        "growth_rate": trend.growth_rate,
        "market_size": trend.market_size,
        "trend_direction": trend.trend_direction,
        "confidence_level": trend.confidence_level,
        "status": trend.status,
        "keywords": trend.keywords,
    }
