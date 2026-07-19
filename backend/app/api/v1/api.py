"""
Main API router for v1 endpoints.

This module aggregates all API routers for the v1 version of the API.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    competitors,
    activities,
    products,
    news,
    market,
    alerts,
    users,
    auth,
    reports,
    searches,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["Competitors"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(market.router, prefix="/market", tags=["Market"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(searches.router, prefix="/searches", tags=["Searches"])

__all__ = ["api_router"]
