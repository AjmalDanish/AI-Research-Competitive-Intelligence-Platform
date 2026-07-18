"""
Competitor product tracking endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.competitor import CompetitorProduct
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    competitor_id: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List competitor products with filtering and pagination.
    """
    query = select(CompetitorProduct)
    
    if competitor_id:
        query = query.where(CompetitorProduct.competitor_id == competitor_id)
    
    if category:
        query = query.where(CompetitorProduct.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "products": [
            {
                "id": product.id,
                "competitor_id": product.competitor_id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "pricing_model": product.pricing_model,
                "price_range": product.price_range,
                "status": product.status,
            }
            for product in products
        ],
        "total": len(products),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(
    competitor_id: int,
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    pricing_model: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new competitor product.
    """
    product = CompetitorProduct(
        competitor_id=competitor_id,
        name=name,
        description=description,
        category=category,
        pricing_model=pricing_model,
    )
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    logger.info(f"New product created: {product.name}")
    
    return {
        "id": product.id,
        "message": "Product created successfully",
    }


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product by ID with full details.
    """
    result = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {
        "id": product.id,
        "competitor_id": product.competitor_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "version": product.version,
        "pricing_model": product.pricing_model,
        "price_range": product.price_range,
        "status": product.status,
        "product_url": product.product_url,
        "popularity_score": product.popularity_score,
    }