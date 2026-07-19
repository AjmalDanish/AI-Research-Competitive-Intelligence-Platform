"""
API endpoint routers.
"""

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.competitors import router as competitors_router
from app.api.v1.endpoints.activities import router as activities_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.news import router as news_router
from app.api.v1.endpoints.market import router as market_router
from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.searches import router as searches_router

__all__ = [
    "health_router",
    "auth_router",
    "users_router",
    "competitors_router",
    "activities_router",
    "products_router",
    "news_router",
    "market_router",
    "alerts_router",
    "reports_router",
    "searches_router",
    "health",
    "auth",
    "users",
    "competitors",
    "activities",
    "products",
    "news",
    "market",
    "alerts",
    "reports",
    "searches",
]
