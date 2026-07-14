"""
Saved search endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.alert import SavedSearch
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_searches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List saved searches with filtering and pagination.
    """
    query = select(SavedSearch)
    
    if category:
        query = query.where(SavedSearch.category == category)
    
    query = query.order_by(SavedSearch.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    searches = result.scalars().all()
    
    return {
        "searches": [
            {
                "id": search.id,
                "user_id": search.user_id,
                "name": search.name,
                "description": search.description,
                "category": search.category,
                "alert_enabled": search.alert_enabled,
                "usage_count": search.usage_count,
                "last_accessed": search.last_accessed,
                "created_at": search.created_at,
            }
            for search in searches
        ],
        "total": len(searches),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_search(
    user_id: int,
    name: str,
    query: dict,
    description: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new saved search.
    """
    search = SavedSearch(
        user_id=user_id,
        name=name,
        description=description,
        query=query,
        category=category,
        alert_enabled=False,
    )
    
    db.add(search)
    await db.commit()
    await db.refresh(search)
    
    logger.info(f"New saved search created: {search.name}")
    
    return {
        "id": search.id,
        "message": "Saved search created successfully",
    }


@router.get("/{search_id}")
async def get_search(
    search_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get saved search by ID with full details.
    """
    result = await db.execute(
        select(SavedSearch).where(SavedSearch.id == search_id)
    )
    search = result.scalar_one_or_none()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found"
        )
    
    # Update usage count and last accessed
    search.usage_count += 1
    from datetime import datetime
    search.last_accessed = datetime.utcnow()
    await db.commit()
    
    return {
        "id": search.id,
        "user_id": search.user_id,
        "name": search.name,
        "description": search.description,
        "query": search.query,
        "filters": search.filters,
        "sort": search.sort,
        "category": search.category,
        "tags": search.tags,
        "alert_enabled": search.alert_enabled,
        "usage_count": search.usage_count,
        "created_at": search.created_at,
    }


@router.delete("/{search_id}")
async def delete_search(
    search_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete saved search by ID.
    """
    result = await db.execute(
        select(SavedSearch).where(SavedSearch.id == search_id)
    )
    search = result.scalar_one_or_none()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found"
        )
    
    await db.delete(search)
    await db.commit()
    
    logger.info(f"Saved search deleted: {search.name}")
    
    return {"message": "Saved search deleted successfully"}