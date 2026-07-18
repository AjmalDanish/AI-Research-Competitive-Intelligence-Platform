"""
Competitor activity tracking endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.competitor import CompetitorActivity
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    competitor_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List competitor activities with filtering and pagination.
    """
    query = select(CompetitorActivity)
    
    if competitor_id:
        query = query.where(CompetitorActivity.competitor_id == competitor_id)
    
    if activity_type:
        query = query.where(CompetitorActivity.activity_type == activity_type)
    
    query = query.order_by(CompetitorActivity.detected_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return {
        "activities": [
            {
                "id": activity.id,
                "competitor_id": activity.competitor_id,
                "activity_type": activity.activity_type,
                "title": activity.title,
                "description": activity.description,
                "activity_date": activity.activity_date,
                "detected_date": activity.detected_date,
                "source_url": activity.source_url,
                "impact_level": activity.impact_level,
                "processed": activity.processed,
            }
            for activity in activities
        ],
        "total": len(activities),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_activity(
    competitor_id: int,
    activity_type: str,
    title: str,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new competitor activity.
    """
    activity = CompetitorActivity(
        competitor_id=competitor_id,
        activity_type=activity_type,
        title=title,
        description=description,
        source_url=source_url,
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    logger.info(f"New activity created: {activity.title}")
    
    return {
        "id": activity.id,
        "message": "Activity created successfully",
    }


@router.get("/{activity_id}")
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity by ID with full details.
    """
    result = await db.execute(
        select(CompetitorActivity).where(CompetitorActivity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    return {
        "id": activity.id,
        "competitor_id": activity.competitor_id,
        "activity_type": activity.activity_type,
        "title": activity.title,
        "description": activity.description,
        "activity_date": activity.activity_date,
        "detected_date": activity.detected_date,
        "source_url": activity.source_url,
        "source_type": activity.source_type,
        "impact_level": activity.impact_level,
        "market_impact": activity.market_impact,
        "processed": activity.processed,
        "verified": activity.verified,
        "metadata": activity.metadata,
    }