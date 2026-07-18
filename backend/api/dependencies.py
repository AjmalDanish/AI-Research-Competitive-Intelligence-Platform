"""
API Dependencies Module

FastAPI dependency injection functions.

Purpose:
- Provide dependency injection setup
- Enable request-scoped dependencies
- Support testing with overrides
- Clean access to infrastructure components

Clean Architecture:
- Interface layer (API)
- No business logic
- Pure dependency wiring
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.models import ErrorResponse
from backend.config.logging import get_logger, logger
from backend.config.settings import get_settings
from backend.database import close_database, get_session, init_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the FastAPI application.
    
    Yields:
        None
    """
    # Startup
    logger.info(
        f"Starting application: {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENVIRONMENT} environment"
    )
    
    try:
        # Initialize database
        await init_database()
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.critical(f"Application startup failed: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down application")
        await close_database()
        logger.info("Application shutdown completed")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    This function creates a FastAPI application with all necessary
    middleware, exception handlers, and routes configured.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url=settings.DOCS_URL if settings.DOCS_ENABLED else None,
        redoc_url=settings.REDOC_URL if settings.DOCS_ENABLED else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    _configure_cors(app)
    
    # Configure exception handlers
    _configure_exception_handlers(app)
    
    # Configure routes
    _configure_routes(app)
    
    # Configure middleware
    _configure_middleware(app)
    
    return app


def _configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware.
    
    Args:
        app: FastAPI application
    """
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    logger.info(f"CORS configured: origins={settings.CORS_ORIGINS}")


def _configure_exception_handlers(app: FastAPI) -> None:
    """
    Configure exception handlers.
    
    Args:
        app: FastAPI application
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle validation errors."""
        logger.warning(
            f"Validation error at {request.url.path}: {exc.errors()}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "detail": str(exc),
                "errors": exc.errors(),
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        logger.error(
            f"Unhandled exception at {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "detail": str(exc) if settings.DEBUG else None,
            },
        )


def _configure_routes(app: FastAPI) -> None:
    """
    Configure API routes.
    
    Args:
        app: FastAPI application
    """
    from backend.api.routes import ROUTES, HEALTH_PATH_PREFIX
    
    for router, tag, description in ROUTES:
        if tag == "health":
            # Health router has special path
            app.include_router(
                router,
                prefix=settings.API_V1_PREFIX + HEALTH_PATH_PREFIX,
                tags=[tag]
            )
        else:
            app.include_router(router, prefix=settings.API_V1_PREFIX, tags=[tag])
        logger.info(f"Registered route: {tag} - {description}")
    
    logger.info("All routes registered")


def _configure_middleware(app: FastAPI) -> None:
    """
    Configure additional middleware.
    
    Args:
        app: FastAPI application
    """
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        """Log all requests."""
        client = request.client.host if request.client else "unknown"
        logger.info(
            f"Incoming request: {request.method} {request.url.path} from {client}"
        )
        
        response = await call_next(request)
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}"
        )
        
        return response


# Export for easy import
__all__ = ["create_app", "lifespan"]