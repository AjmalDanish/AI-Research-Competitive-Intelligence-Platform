"""
Alert and notification endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.db.session import get_db
from app.models.alert import Alert, AlertRule
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy import select

router = APIRouter()
logger = get_logger(__name__)


async def get_current_user_object(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user object from JWT token.
    
    Args:
        user_id: Current user ID from JWT token
        db: Database session
        
    Returns:
        User: Current user object
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# Pydantic models for request/response
class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    alert_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    read: Optional[bool] = None


class AlertCreate(BaseModel):
    title: str
    message: Optional[str] = None
    alert_type: str
    priority: str = "medium"
    status: str = "pending"


@router.get("")
@router.get("")
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    """
    List alerts with filtering and pagination.
    """
    try:
        query = select(Alert).where(Alert.user_id == current_user.id)
        
        if status:
            query = query.where(Alert.status == status)
        
        if priority:
            query = query.where(Alert.priority == priority)
        
        query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        # Convert alerts to safe format, handling potential enum issues
        safe_alerts = []
        for alert in alerts:
            try:
                safe_alert = {
                    "id": alert.id,
                    "user_id": alert.user_id,
                    "title": alert.title,
                    "message": alert.message,
                    "alert_type": str(alert.alert_type) if alert.alert_type else "custom",
                    "priority": str(alert.priority) if alert.priority else "medium",
                    "status": str(alert.status) if alert.status else "pending",
                    "read": alert.read,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                }
                safe_alerts.append(safe_alert)
            except Exception as e:
                logger.warning(f"Skipping alert {alert.id} due to error: {e}")
                continue
        
        return {
            "alerts": safe_alerts,
            "total": len(safe_alerts),
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        # Return empty list on error instead of crashing
        return {
            "alerts": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
        }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert.
    """
    alert = Alert(
        user_id=current_user.id,
        title=alert_data.title,
        message=alert_data.message or "",
        alert_type=alert_data.alert_type,
        priority=alert_data.priority,
        status=alert_data.status,
        read=False,
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    logger.info(f"New alert created: {alert.title}")
    
    return {
        "id": alert.id,
        "message": "Alert created successfully",
    }


@router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields that are provided
    if alert_update.title is not None:
        alert.title = alert_update.title
    if alert_update.message is not None:
        alert.message = alert_update.message
    if alert_update.alert_type is not None:
        alert.alert_type = alert_update.alert_type
    if alert_update.priority is not None:
        alert.priority = alert_update.priority
    if alert_update.status is not None:
        alert.status = alert_update.status
    if alert_update.read is not None:
        alert.read = alert_update.read
    
    await db.commit()
    await db.refresh(alert)
    
    logger.info(f"Alert updated: {alert.title}")
    
    return {
        "id": alert.id,
        "title": alert.title,
        "message": alert.message,
        "alert_type": alert.alert_type,
        "priority": alert.priority,
        "status": alert.status,
        "read": alert.read,
    }


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await db.delete(alert)
    await db.commit()
    
    logger.info(f"Alert deleted: {alert.title}")
    
    return {"message": "Alert deleted successfully"}


@router.put("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an alert as read.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.read = True
    await db.commit()
    
    return {"message": "Alert marked as read"}


@router.get("/rules")
async def list_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List alert rules with pagination.
    """
    query = select(AlertRule).offset(skip).limit(limit)
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return {
        "rules": [
            {
                "id": rule.id,
                "user_id": rule.user_id,
                "name": rule.name,
                "description": rule.description,
                "alert_type": rule.alert_type,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "trigger_count": rule.trigger_count,
                "created_at": rule.created_at,
            }
            for rule in rules
        ],
        "total": len(rules),
        "skip": skip,
        "limit": limit,
    }


@router.post("/rules", status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    user_id: int,
    name: str,
    alert_type: str,
    conditions: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert rule.
    """
    rule = AlertRule(
        user_id=user_id,
        name=name,
        alert_type=alert_type,
        conditions=conditions,
        is_active=True,
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    logger.info(f"New alert rule created: {rule.name}")
    
    return {
        "id": rule.id,
        "message": "Alert rule created successfully",
    }