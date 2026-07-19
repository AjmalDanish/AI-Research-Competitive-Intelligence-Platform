"""
CORS configuration for production deployment.
"""

from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


class CORSConfig:
    """CORS configuration settings."""

    ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOW_HEADERS: List[str] = ["*"]
    EXPOSE_HEADERS: List[str] = ["Content-Length", "Content-Type"]
    MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", "600"))


def configure_cors(app: FastAPI, config: Optional[CORSConfig] = None) -> None:
    """
    Configure CORS for FastAPI application.

    Args:
        app: FastAPI application instance
        config: CORS configuration (uses default if not provided)
    """
    if config is None:
        config = CORSConfig()

    # Handle wildcard origins
    allow_origins = config.ORIGINS if "*" not in config.ORIGINS else ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=config.ALLOW_CREDENTIALS,
        allow_methods=config.ALLOW_METHODS,
        allow_headers=config.ALLOW_HEADERS,
        expose_headers=config.EXPOSE_HEADERS,
        max_age=config.MAX_AGE,
    )


def get_cors_origins() -> List[str]:
    """Get configured CORS origins."""
    origins = os.getenv("CORS_ORIGINS", "*").split(",")
    return origins if "*" not in origins else ["*"]


__all__ = [
    "CORSConfig",
    "configure_cors",
    "get_cors_origins",
]
