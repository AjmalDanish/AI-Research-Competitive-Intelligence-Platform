"""
Database Module

Database layer with connection management and models.

This module contains all database-related code:

- connection: Database connection and session management
- base: SQLAlchemy declarative base and mixins

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure database operations
"""

from backend.database.base import Base, SoftDeleteMixin, TimestampMixin
from backend.database.connection import (
    check_database_health,
    close_database,
    get_engine,
    get_session,
    get_session_maker,
    init_database,
)

# Export for easy import
__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "get_engine",
    "get_session_maker",
    "get_session",
    "init_database",
    "close_database",
    "check_database_health",
]