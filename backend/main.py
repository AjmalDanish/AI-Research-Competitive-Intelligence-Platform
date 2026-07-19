"""
AI Website Intelligence Platform

FastAPI application entry point.

Purpose:
- Initialize FastAPI application
- Configure middleware and routes
- Serve as application entry point

Clean Architecture:
- Infrastructure layer
- No business logic
- Application bootstrap only
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from backend.api.dependencies import create_app
from backend.config.logging import logger
from backend.config.settings import get_settings
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = get_settings()

# Create FastAPI application
app = create_app()


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """
    Root endpoint redirects to API documentation.

    Returns:
        RedirectResponse: Redirects to /docs
    """
    return RedirectResponse(url=settings.DOCS_URL)


# Note: Startup and shutdown events are handled in the lifespan context manager
# in backend/api/dependencies.py to avoid deprecated @app.on_event decorators


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
