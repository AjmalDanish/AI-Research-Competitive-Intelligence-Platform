"""
Utils Module

Utility functions and helpers.

This module contains utility code:

- exceptions: Custom exception classes
- logger: Logging utilities

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure utility functions
"""

from backend.utils.exceptions import (
    BaseApplicationException,
    ConfigurationException,
    ConflictException,
    DatabaseException,
    ExternalServiceException,
    NotFoundException,
    ValidationException,
)
from backend.utils.logger import get_logger

# Export for easy import
__all__ = [
    "BaseApplicationException",
    "ValidationException",
    "NotFoundException",
    "ConflictException",
    "DatabaseException",
    "ConfigurationException",
    "ExternalServiceException",
    "get_logger",
]
