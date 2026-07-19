"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db, check_db_connection
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.common import HealthResponse, MessageResponse

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns the overall health status of the API.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
        services={},
    )


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with service status.

    Checks database connection and other service dependencies.
    """
    services = {
        "api": {"status": "healthy", "timestamp": datetime.utcnow().isoformat()},
    }

    # Check database connection
    try:
        db_healthy = await check_db_connection()
        services["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Check Redis (if configured)
    # This would be implemented when Redis is integrated

    overall_status = (
        "healthy" if all(svc["status"] == "healthy" for svc in services.values()) else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
        services=services,
    )


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check for Kubernetes/container orchestration.

    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Check if we can execute a simple query
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/liveness")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.

    Returns 200 if the service is alive.
    """
    return {"status": "alive"}


@router.get("/version")
async def get_version():
    """
    Get API version information.
    """
    return {
        "version": settings.VERSION,
        "name": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
    }


@router.get("/config", response_model=dict)
async def get_public_config():
    """
    Get public configuration information.

    Returns non-sensitive configuration values.
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "api_version": "v1",
        "features": {
            "user_management": True,
            "competitor_tracking": True,
            "market_intelligence": True,
            "alerts": True,
            "reports": True,
        },
    }
