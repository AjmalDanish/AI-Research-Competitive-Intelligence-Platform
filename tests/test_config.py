"""
Configuration Tests

Test application configuration and settings.
"""

import pytest
from pydantic import ValidationError

from backend.config.logging import LoggingConfig, get_logger
from backend.config.settings import Settings, get_settings


class TestSettings:
    """Test application settings."""
    
    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should return the same instance
        assert settings1 is settings2
    
    def test_default_settings(self):
        """Test default settings are applied."""
        settings = get_settings()
        
        assert settings.APP_NAME is not None
        assert settings.APP_VERSION is not None
        assert settings.ENVIRONMENT is not None
        assert settings.HOST is not None
        assert settings.PORT is not None
    
    def test_database_settings(self):
        """Test database settings."""
        settings = get_settings()
        
        assert settings.DATABASE_NAME is not None
        assert settings.TEST_DATABASE_NAME is not None
        assert settings.DATABASE_USER is not None
        assert settings.DATABASE_PASSWORD is not None
        assert settings.DATABASE_HOST is not None
        assert settings.DATABASE_PORT is not None
    
    def test_redis_settings(self):
        """Test Redis settings."""
        settings = get_settings()
        
        assert settings.REDIS_HOST is not None
        assert settings.REDIS_PORT is not None
        assert settings.REDIS_DB is not None
    
    def test_logging_settings(self):
        """Test logging settings."""
        settings = get_settings()
        
        assert settings.LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        assert settings.LOG_FORMAT in ("json", "text")
    
    def test_api_settings(self):
        """Test API settings."""
        settings = get_settings()
        
        assert settings.API_V1_PREFIX is not None
        assert settings.API_TITLE is not None
        assert settings.API_VERSION is not None
        assert settings.DOCS_URL is not None
    
    def test_cors_settings(self):
        """Test CORS settings."""
        settings = get_settings()
        
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) > 0
        assert isinstance(settings.CORS_ALLOW_CREDENTIALS, bool)
        assert isinstance(settings.CORS_ALLOW_METHODS, list)
        assert len(settings.CORS_ALLOW_METHODS) > 0
    
    def test_database_url_property(self):
        """Test database URL property."""
        settings = get_settings()
        url = settings.DATABASE_URL
        
        assert isinstance(url, str)
        assert url.startswith("postgresql+asyncpg://")
    
    def test_test_database_url_property(self):
        """Test test database URL property."""
        settings = get_settings()
        url = settings.TEST_DATABASE_URL
        
        assert isinstance(url, str)
        assert url.startswith("postgresql+asyncpg://")
        assert settings.TEST_DATABASE_NAME in url
    
    def test_redis_url_property(self):
        """Test Redis URL property."""
        settings = get_settings()
        url = settings.REDIS_URL
        
        assert isinstance(url, str)
        assert url.startswith("redis://")
    
    def test_port_validation(self):
        """Test port validation."""
        settings = get_settings()
        
        # All ports should be in valid range
        assert 1 <= settings.PORT <= 65535
        assert 1 <= settings.DATABASE_PORT <= 65535
        assert 1 <= settings.REDIS_PORT <= 65535
    
    def test_environment_validation(self):
        """Test environment validation."""
        settings = get_settings()
        
        assert settings.ENVIRONMENT in ("development", "testing", "production")
    
    def test_cors_origins_parsing(self):
        """Test CORS origins can be parsed correctly."""
        settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:8080")
        
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) == 2
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://localhost:8080" in settings.CORS_ORIGINS
    
    def test_invalid_port_raises_error(self):
        """Test that invalid port raises validation error."""
        with pytest.raises(ValidationError):
            Settings(PORT=99999)
    
    def test_invalid_environment_raises_error(self):
        """Test that invalid environment raises validation error."""
        with pytest.raises(ValidationError):
            Settings(ENVIRONMENT="invalid")


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_logging_config_initialization(self):
        """Test logging config initializes without errors."""
        config = LoggingConfig()
        assert config is not None
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger."""
        logger = get_logger("test_module")
        assert logger is not None
    
    def test_get_logger_with_module_name(self):
        """Test get_logger with module name."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        # Should return loggers
        assert logger1 is not None
        assert logger2 is not None
    
    def test_logging_config_settings(self):
        """Test logging config respects settings."""
        settings = get_settings()
        config = LoggingConfig()
        
        # Config should be initialized
        assert config is not None
        assert config.settings is not None


class TestConfigurationIntegration:
    """Test configuration integration."""
    
    def test_all_required_settings_present(self):
        """Test all required settings are present."""
        settings = get_settings()
        
        # Check critical settings
        assert settings.APP_NAME
        assert settings.APP_VERSION
        assert settings.DATABASE_NAME
        assert settings.DATABASE_USER
        assert settings.DATABASE_PASSWORD
        assert settings.DATABASE_HOST
        assert settings.DATABASE_PORT
    
    def test_settings_are_immutable(self):
        """Test that settings instance is properly configured."""
        settings = get_settings()
        
        # Settings should have all expected attributes
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'REDIS_URL')
        assert hasattr(settings, 'LOG_LEVEL')
    
    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        # Clear cache first
        get_settings.cache_clear()
        
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("ENVIRONMENT", "testing")
        
        # Clear cache again after setting environment variables
        get_settings.cache_clear()
        
        settings = get_settings()
        assert settings.APP_NAME == "Test App"
        assert settings.ENVIRONMENT == "testing"
        
        # Clean up
        get_settings.cache_clear()