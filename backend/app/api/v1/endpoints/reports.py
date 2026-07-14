"""
Report generation and management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.alert import Report
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List reports with filtering and pagination.
    """
    query = select(Report)
    
    if report_type:
        query = query.where(Report.report_type == report_type)
    
    if status:
        query = query.where(Report.status == status)
    
    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return {
        "reports": [
            {
                "id": report.id,
                "user_id": report.user_id,
                "title": report.title,
                "description": report.description,
                "report_type": report.report_type,
                "status": report.status,
                "is_public": report.is_public,
                "created_at": report.created_at,
                "generated_at": report.generated_at,
            }
            for report in reports
        ],
        "total": len(reports),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    user_id: int,
    title: str,
    report_type: str,
    description: Optional[str] = None,
    parameters: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new report.
    """
    report = Report(
        user_id=user_id,
        title=title,
        description=description,
        report_type=report_type,
        parameters=parameters or {},
        status="draft",
        is_public=False,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"New report created: {report.title}")
    
    return {
        "id": report.id,
        "message": "Report created successfully",
    }


@router.post("/{report_id}/generate")
async def generate_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a report.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.status = "generating"
    await db.commit()
    
    # In a real implementation, this would trigger async report generation
    # For now, we'll mark it as completed
    
    from datetime import datetime
    report.status = "completed"
    report.generated_at = datetime.utcnow()
    report.content = {
        "summary": "Sample report content",
        "insights": ["Insight 1", "Insight 2", "Insight 3"],
    }
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"Report generated: {report.title}")
    
    return {
        "id": report.id,
        "status": report.status,
        "message": "Report generated successfully",
    }


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get report by ID with full details.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {
        "id": report.id,
        "user_id": report.user_id,
        "title": report.title,
        "description": report.description,
        "report_type": report.report_type,
        "content": report.content,
        "summary": report.summary,
        "insights": report.insights,
        "parameters": report.parameters,
        "status": report.status,
        "is_public": report.is_public,
        "created_at": report.created_at,
        "generated_at": report.generated_at,
    }