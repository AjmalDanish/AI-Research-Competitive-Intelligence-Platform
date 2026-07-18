"""
Health Check Endpoints

Comprehensive health check endpoints for monitoring.

Purpose:
- Provide health status monitoring
- Support Kubernetes/Docker health checks
- Enable infrastructure monitoring
- Help with debugging

Clean Architecture:
- Interface layer (API)
- No business logic
- Infrastructure monitoring only
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Response, status

from backend.api.models import HealthResponse
from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.database import check_database_health

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="General health check",
    description="Check overall system health",
)
async def health_check() -> HealthResponse:
    """
    General health check endpoint.
    
    Returns the overall health status of the system.
    This endpoint is suitable for load balancer health checks.
    
    Returns:
        HealthResponse: System health information
    """
    checks = {}
    
    # Check database health
    db_healthy = await check_database_health()
    checks["database"] = "healthy" if db_healthy else "unhealthy"
    
    # Determine overall status
    overall_status = (
        "healthy"
        if all(check == "healthy" for check in checks.values())
        else "unhealthy"
    )
    
    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        checks=checks,
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Readiness probe",
    description="Check if the system is ready to accept traffic",
)
async def readiness_check(response: Response) -> HealthResponse:
    """
    Readiness probe endpoint.
    
    Returns whether the system is ready to accept traffic.
    This endpoint is suitable for Kubernetes readiness probes.
    
    Returns:
        HealthResponse: Readiness status
    """
    checks = {}
    overall_status = "healthy"
    http_status = status.HTTP_200_OK
    
    # Check database health (required for readiness)
    db_healthy = await check_database_health()
    checks["database"] = "healthy" if db_healthy else "unhealthy"
    
    if not db_healthy:
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.warning("Readiness check failed: database unhealthy")
    
    response.status_code = http_status
    
    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        checks=checks,
    )


@router.get(
    "/live",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Check if the system is running",
)
async def liveness_check() -> HealthResponse:
    """
    Liveness probe endpoint.
    
    Returns whether the system is alive.
    This endpoint is suitable for Kubernetes liveness probes.
    A simple liveness check indicates the process is running.
    
    Returns:
        HealthResponse: Liveness status
    """
    # Simple liveness check - if we can respond, we're alive
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        checks={},
    )


@router.get(
    "/db",
    response_model=HealthResponse,
    summary="Database health check",
    description="Check database connectivity",
)
async def database_health_check(response: Response) -> HealthResponse:
    """
    Database health check endpoint.
    
    Returns the health status of the database connection.
    
    Returns:
        HealthResponse: Database health information
    """
    db_healthy = await check_database_health()
    
    if not db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.error("Database health check failed")
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        checks={
            "database": "healthy" if db_healthy else "unhealthy",
        },
    )


# Export for easy import
__all__ = ["router"]