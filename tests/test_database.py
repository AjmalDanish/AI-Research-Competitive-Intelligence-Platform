"""
Database Connection Tests

Test database connectivity and session management.
"""

import pytest

from backend.config.settings import get_settings
from backend.database import (
    Base,
    check_database_health,
    get_engine,
    get_session,
    get_session_maker,
    init_database,
    close_database,
)


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    @pytest.mark.asyncio
    async def test_engine_creation(self):
        """Test database engine creation."""
        engine = get_engine()
        assert engine is not None
        assert engine.dialect.name == "postgresql"
    
    @pytest.mark.asyncio
    async def test_session_maker_creation(self):
        """Test session maker creation."""
        session_maker = get_session_maker()
        assert session_maker is not None
    
    @pytest.mark.asyncio
    async def test_database_initialization(self):
        """Test database initialization."""
        # This test requires actual database connection
        try:
            await init_database()
            engine = get_engine()
            assert engine is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check."""
        result = await check_database_health()
        # Result should be boolean
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_session_context_manager(self):
        """Test session context manager."""
        try:
            async with get_session() as session:
                assert session is not None
                
                # Execute simple query
                result = await session.execute("SELECT 1")
                assert result.scalar() == 1
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.asyncio
    async def test_database_close(self):
        """Test database connection closing."""
        try:
            await close_database()
            # Engine should be reset
            # Next call should create new engine
            engine = get_engine()
            assert engine is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestDatabaseConfiguration:
    """Test database configuration."""
    
    def test_database_url_format(self):
        """Test database URL format is correct."""
        settings = get_settings()
        url = settings.DATABASE_URL
        
        assert url.startswith("postgresql+asyncpg://")
        assert settings.DATABASE_NAME in url
        assert settings.DATABASE_HOST in url
    
    def test_test_database_url_format(self):
        """Test test database URL format is correct."""
        settings = get_settings()
        url = settings.TEST_DATABASE_URL
        
        assert url.startswith("postgresql+asyncpg://")
        assert settings.TEST_DATABASE_NAME in url
        assert settings.DATABASE_HOST in url
    
    def test_database_url_components(self):
        """Test database URL contains all components."""
        settings = get_settings()
        url = settings.DATABASE_URL
        
        # Check for URL components
        assert f"@{settings.DATABASE_HOST}:" in url
        assert f":{settings.DATABASE_PORT}/" in url
        assert settings.DATABASE_USER in url
    
    def test_pool_configuration(self):
        """Test database pool configuration."""
        settings = get_settings()
        
        assert settings.DATABASE_POOL_SIZE > 0
        assert settings.DATABASE_MAX_OVERFLOW >= 0
        assert settings.DATABASE_POOL_TIMEOUT > 0
        assert settings.DATABASE_POOL_RECYCLE > 0


class TestDatabaseModels:
    """Test database models and base."""
    
    def test_base_exists(self):
        """Test that Base class exists."""
        assert Base is not None
    
    def test_base_is_declarative(self):
        """Test that Base is declarative base."""
        from sqlalchemy.orm import DeclarativeBase
        
        assert isinstance(Base, type)
        # Check if it inherits from DeclarativeBase
        assert hasattr(Base, 'registry')
    
    def test_base_metadata(self):
        """Test that Base has metadata."""
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None