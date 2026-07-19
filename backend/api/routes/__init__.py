"""
API Routes Module

FastAPI route definitions.

This module contains all API route definitions:

- health: Health check endpoints

Clean Architecture:
- Interface layer (API)
- No business logic
- Pure route definitions
"""

from backend.api.routes.health import router as health_router

# Route registry
ROUTES = [
    (health_router, "health", "Health check endpoints"),
]

# Health router path prefix
HEALTH_PATH_PREFIX = "/health"


# Export for easy import
__all__ = ["ROUTES", "health_router"]
