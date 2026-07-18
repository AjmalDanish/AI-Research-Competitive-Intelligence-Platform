"""
Configuration Module

Application configuration management.

This module contains all configuration-related code:

- settings: Application settings and environment variables
- logging: Logging configuration and setup

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure configuration management
"""

from backend.config.logging import LoggingConfig, logger

def get_logger(name: str):
    """Get logger instance."""
    return LoggingConfig.get_logger(name)
from backend.config.settings import Settings, get_settings

# Export for easy import
__all__ = [
    "Settings",
    "get_settings",
    "LoggingConfig",
    "get_logger",
    "logger",
]