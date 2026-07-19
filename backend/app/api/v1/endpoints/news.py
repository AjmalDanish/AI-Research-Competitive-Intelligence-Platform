"""
Competitor news tracking endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.competitor import CompetitorNews
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    competitor_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List competitor news with filtering and pagination.
    """
    query = select(CompetitorNews)

    if competitor_id:
        query = query.where(CompetitorNews.competitor_id == competitor_id)

    if sentiment:
        query = query.where(CompetitorNews.sentiment == sentiment)

    query = query.order_by(CompetitorNews.publish_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    news_items = result.scalars().all()

    return {
        "news": [
            {
                "id": news.id,
                "competitor_id": news.competitor_id,
                "title": news.title,
                "summary": news.summary,
                "source_name": news.source_name,
                "source_url": news.source_url,
                "publish_date": news.publish_date,
                "sentiment": news.sentiment,
                "category": news.category,
            }
            for news in news_items
        ],
        "total": len(news_items),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_news(
    competitor_id: int,
    title: str,
    source_url: str,
    summary: Optional[str] = None,
    source_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new competitor news article.
    """
    news = CompetitorNews(
        competitor_id=competitor_id,
        title=title,
        source_url=source_url,
        summary=summary,
        source_name=source_name,
    )

    db.add(news)
    await db.commit()
    await db.refresh(news)

    logger.info(f"New news article created: {news.title}")

    return {
        "id": news.id,
        "message": "News article created successfully",
    }


@router.get("/{news_id}")
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get news article by ID with full details.
    """
    result = await db.execute(select(CompetitorNews).where(CompetitorNews.id == news_id))
    news = result.scalar_one_or_none()

    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found")

    return {
        "id": news.id,
        "competitor_id": news.competitor_id,
        "title": news.title,
        "summary": news.summary,
        "content": news.content,
        "source_name": news.source_name,
        "source_url": news.source_url,
        "author": news.author,
        "publish_date": news.publish_date,
        "sentiment": news.sentiment,
        "sentiment_score": news.sentiment_score,
        "category": news.category,
        "tags": news.tags,
        "processed": news.processed,
    }
