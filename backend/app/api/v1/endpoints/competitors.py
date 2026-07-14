"""
Competitor tracking endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.db.session import get_db
from app.models.competitor import Competitor
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_competitors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all competitors with filtering and pagination.
    """
    query = select(Competitor)
    
    if industry:
        query = query.where(Competitor.industry == industry)
    
    if status:
        query = query.where(Competitor.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    competitors = result.scalars().all()
    
    return {
        "competitors": [
            {
                "id": comp.id,
                "name": comp.name,
                "website": comp.website,
                "industry": comp.industry,
                "sector": comp.sector,
                "tier": comp.tier,
                "status": comp.status,
                "employees": comp.employees,
                "revenue": comp.revenue,
                "last_updated": comp.last_updated,
            }
            for comp in competitors
        ],
        "total": len(competitors),
        "skip": skip,
        "limit": limit,
    }


@router.get("/{competitor_id}")
async def get_competitor(
    competitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get competitor by ID with full details.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    return {
        "id": competitor.id,
        "name": competitor.name,
        "website": competitor.website,
        "industry": competitor.industry,
        "sector": competitor.sector,
        "description": competitor.description,
        "founded_year": competitor.founded_year,
        "headquarters": competitor.headquarters,
        "employees": competitor.employees,
        "revenue": competitor.revenue,
        "email": competitor.email,
        "phone": competitor.phone,
        "linkedin_url": competitor.linkedin_url,
        "twitter_handle": competitor.twitter_handle,
        "facebook_url": competitor.facebook_url,
        "tier": competitor.tier,
        "status": competitor.status,
        "last_updated": competitor.last_updated,
        "first_tracked": competitor.first_tracked,
        "tracking_enabled": competitor.tracking_enabled,
        "metadata": competitor.metadata,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_competitor(
    name: str,
    website: Optional[str] = None,
    industry: Optional[str] = None,
    sector: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new competitor to track.
    """
    competitor = Competitor(
        name=name,
        website=website,
        industry=industry,
        sector=sector,
        description=description,
        status="active",
        tier="medium",
    )
    
    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)
    
    logger.info(f"New competitor created: {competitor.name}")
    
    return {
        "id": competitor.id,
        "name": competitor.name,
        "message": "Competitor created successfully",
    }


@router.put("/{competitor_id}")
async def update_competitor(
    competitor_id: int,
    name: Optional[str] = None,
    website: Optional[str] = None,
    industry: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update competitor information.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    if name is not None:
        competitor.name = name
    if website is not None:
        competitor.website = website
    if industry is not None:
        competitor.industry = industry
    if description is not None:
        competitor.description = description
    
    await db.commit()
    await db.refresh(competitor)
    
    logger.info(f"Competitor updated: {competitor.name}")
    
    return {"message": "Competitor updated successfully"}


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete competitor by ID.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    await db.delete(competitor)
    await db.commit()
    
    logger.info(f"Competitor deleted: {competitor.name}")
    
    return {"message": "Competitor deleted successfully"}