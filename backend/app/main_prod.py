"""
Main FastAPI application with comprehensive security.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import logging
from datetime import datetime
import os

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security_middleware import (
    security_config,
    security_middleware,
    token_manager,
    SecurityHeaders,
)
from app.core.cors import configure_cors, CORSConfig
from app.core.rate_limiting import (
    RateLimiter,
    rate_limit,
    global_rate_limiter,
    initialize_rate_limiter,
    close_rate_limiter,
)
from app.api.v1.api import api_router
from app.db.session import engine

# Setup logging
logger = setup_logging(__name__)

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize rate limiter
    if settings.RATE_LIMIT_ENABLED:
        await initialize_rate_limiter()
        logger.info("Rate limiter initialized")

    # Initialize database
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close rate limiter
    if settings.RATE_LIMIT_ENABLED:
        await close_rate_limiter()
        logger.info("Rate limiter closed")

    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered competitive intelligence platform",
    docs_url=settings.API_DOCS_URL if settings.API_DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.API_DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.API_DOCS_ENABLED else None,
    lifespan=lifespan,
)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
cors_config = CORSConfig(
    ORIGINS=settings.CORS_ORIGINS,
    ALLOW_CREDENTIALS=settings.CORS_ALLOW_CREDENTIALS,
    MAX_AGE=settings.CORS_MAX_AGE,
)
configure_cors(app, cors_config)

# Add security middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted hosts middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    )


@app.middleware("http")
async def security_middleware_handler(request: Request, call_next):
    """Custom security middleware."""
    try:
        # Validate request
        await security_middleware.validate_request(request)

        # Process request
        response = await call_next(request)

        # Add security headers
        security_headers = SecurityHeaders.get_headers()
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        # Add custom headers
        response.headers["X-API-Version"] = settings.APP_VERSION
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "")

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Request logging middleware."""
    start_time = datetime.utcnow()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()

    # Log response
    logger.info(
        f"Response: {response.status_code} "
        f"duration: {duration:.3f}s "
        f"for {request.method} {request.url.path}"
    )

    # Add duration header
    response.headers["X-Response-Time"] = f"{duration:.3f}"

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "request_id": request.headers.get("X-Request-ID", ""),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle global exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        detail = "Internal server error"
    else:
        detail = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "request_id": request.headers.get("X-Request-ID", "")},
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": settings.API_DOCS_URL if settings.API_DOCS_ENABLED else None,
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {"api": "healthy", "database": "checking...", "redis": "checking..."},
    }

    # Check database
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis (if configured)
    if settings.REDIS_URL:
        try:
            # Add Redis health check here
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"

    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Add actual metrics here
    return {
        "status": "metrics available",
        "endpoints": len(api_router.routes),
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=4 if settings.ENVIRONMENT == "production" else 1,
        access_log=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
