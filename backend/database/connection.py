"""
Database Connection Module

PostgreSQL async database connection and session management.

Purpose:
- Configure async PostgreSQL connection
- Manage database sessions
- Handle connection pooling
- Provide database health checks

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure database connectivity
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from backend.config.logging import get_logger
from backend.config.settings import get_settings

logger = get_logger(__name__)

# Global database engine and session factory
_engine = None
_async_session_maker = None


def get_engine():
    """
    Get or create database engine.

    Returns:
        AsyncEngine: SQLAlchemy async engine
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        # Determine database URL based on environment
        if settings.ENVIRONMENT == "testing":
            database_url = settings.TEST_DATABASE_URL
            logger.info(f"Using test database: {settings.TEST_DATABASE_NAME}")
        else:
            database_url = settings.DATABASE_URL
            logger.info(f"Using main database: {settings.DATABASE_NAME}")

        # Create async engine
        # Note: NullPool doesn't accept pool configuration parameters
        if settings.ENVIRONMENT == "testing":
            _engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                poolclass=NullPool,
            )
        else:
            _engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=settings.DATABASE_POOL_RECYCLE,
            )

        logger.info(
            f"Database engine created: {settings.DATABASE_HOST}:{settings.DATABASE_PORT} "
            f"(pool_size={settings.DATABASE_POOL_SIZE}, max_overflow={settings.DATABASE_MAX_OVERFLOW})"
        )

    return _engine


def get_session_maker():
    """
    Get or create session maker.

    Returns:
        async_sessionmaker: SQLAlchemy session factory
    """
    global _async_session_maker

    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Session maker created")

    return _async_session_maker


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session context manager.

    This function provides a context manager for database sessions.
    Sessions are automatically committed on success and rolled back on failure.

    Yields:
        AsyncSession: Database session

    Example:
        async with get_session() as session:
            result = await session.execute(query)
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Session rolled back due to exception")
            raise
        finally:
            await session.close()


async def init_database():
    """
    Initialize database connection.

    This function should be called during application startup.
    It establishes the database connection and validates connectivity.
    """
    try:
        engine = get_engine()
        session_maker = get_session_maker()

        # Test connection by executing a simple query
        async with session_maker() as session:
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))

        logger.info("Database connection established successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


async def close_database():
    """
    Close database connection.

    This function should be called during application shutdown.
    It properly closes the database connection and disposes the engine.
    """
    global _engine, _async_session_maker

    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database connection closed")

    if _async_session_maker:
        _async_session_maker = None

    logger.info("Database resources disposed")


async def check_database_health() -> bool:
    """
    Check database health.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        engine = get_engine()
        session_maker = get_session_maker()

        async with session_maker() as session:
            result = await session.execute("SELECT 1")
            result.scalar()

        return True

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


# Export for easy import
__all__ = [
    "get_engine",
    "get_session_maker",
    "get_session",
    "init_database",
    "close_database",
    "check_database_health",
]
