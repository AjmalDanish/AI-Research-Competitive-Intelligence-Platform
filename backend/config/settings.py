"""
Application Settings Module

Configuration management using Pydantic Settings with environment variable support.

Purpose:
- Centralize all configuration
- Type-safe configuration
- Environment variable support
- Validation of configuration values

Clean Architecture:
- Infrastructure layer
- No business logic
- Dependency-free configuration
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Configuration Sections:
    - Application: General application settings
    - Database: PostgreSQL database configuration
    - Redis: Redis cache configuration
    - Logging: Logging configuration
    - API: API configuration
    - Security: Security settings
    - Future AI Providers: Reserved for future milestones

    Environment variables are loaded from .env file or system environment.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==================== Application ====================
    APP_NAME: str = Field(
        default="AI Website Intelligence Platform", description="Application name"
    )

    APP_VERSION: str = Field(default="0.1.0", description="Application version")

    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development", description="Application environment"
    )

    DEBUG: bool = Field(default=False, description="Debug mode")

    HOST: str = Field(default="0.0.0.0", description="API host")

    PORT: int = Field(default=8000, description="API port")

    # ==================== Database ====================
    DATABASE_NAME: str = Field(
        default="ai_website_intelligence", description="Main database name"
    )

    TEST_DATABASE_NAME: str = Field(
        default="ai_website_intelligence_test", description="Test database name"
    )

    DATABASE_USER: str = Field(default="ai_user", description="Database user")

    DATABASE_PASSWORD: str = Field(
        default="ai_password", description="Database password"
    )

    DATABASE_HOST: str = Field(default="localhost", description="Database host")

    DATABASE_PORT: int = Field(default=5432, description="Database port")

    DATABASE_POOL_SIZE: int = Field(
        default=10, description="Database connection pool size"
    )

    DATABASE_MAX_OVERFLOW: int = Field(
        default=20, description="Database maximum overflow connections"
    )

    DATABASE_POOL_TIMEOUT: int = Field(
        default=30, description="Database connection pool timeout (seconds)"
    )

    DATABASE_POOL_RECYCLE: int = Field(
        default=3600, description="Database connection pool recycle time (seconds)"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def TEST_DATABASE_URL(self) -> str:
        """Construct test database URL from components."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.TEST_DATABASE_NAME}"
        )

    # ==================== Redis ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")

    REDIS_PORT: int = Field(default=6379, description="Redis port")

    REDIS_DB: int = Field(default=0, description="Redis database number")

    REDIS_PASSWORD: str | None = Field(default=None, description="Redis password")

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components."""
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ==================== Logging ====================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    LOG_FORMAT: Literal["json", "text"] = Field(
        default="json", description="Log format"
    )

    LOG_FILE: str | None = Field(
        default=None, description="Log file path (None for stdout only)"
    )

    LOG_ROTATION: str = Field(default="10 MB", description="Log rotation size")

    LOG_RETENTION: str = Field(default="30 days", description="Log retention period")

    # ==================== API ====================
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")

    API_TITLE: str = Field(
        default="AI Website Intelligence Platform API", description="API title"
    )

    API_DESCRIPTION: str = Field(
        default="API for analyzing websites and extracting business intelligence",
        description="API description",
    )

    API_VERSION: str = Field(default="0.1.0", description="API version")

    DOCS_ENABLED: bool = Field(default=True, description="Enable Swagger UI")

    DOCS_URL: str = Field(default="/docs", description="Swagger UI URL")

    REDOC_URL: str = Field(default="/redoc", description="ReDoc URL")

    # ==================== Security ====================
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for signing",
    )

    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration (minutes)"
    )

    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )

    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True, description="CORS allow credentials"
    )

    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "OPTIONS"], description="CORS allowed methods"
    )

    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"], description="CORS allowed headers"
    )

    # ==================== Crawler Configuration ====================
    # User Agent
    CRAWLER_USER_AGENT: str = Field(
        default="AI-Website-Intelligence-Platform/0.1 (+https://github.com/AjmalDanish/AI-Research-Competitive-Intelligence-Platform)",
        description="User agent for crawler requests",
    )

    # Timeout Settings (seconds)
    CRAWLER_TIMEOUT_URL_VALIDATION: int = Field(
        default=5, description="URL validation timeout (seconds)"
    )

    CRAWLER_TIMEOUT_ROBOTS_CHECK: int = Field(
        default=10, description="Robots.txt check timeout (seconds)"
    )

    CRAWLER_TIMEOUT_CRAWL: int = Field(
        default=30, description="Page crawl timeout (seconds)"
    )

    CRAWLER_TIMEOUT_OVERALL: int = Field(
        default=60, description="Overall operation timeout (seconds)"
    )

    # Retry Settings
    CRAWLER_MAX_RETRIES: int = Field(
        default=3, description="Maximum number of retry attempts"
    )

    CRAWLER_RETRY_INITIAL_DELAY: int = Field(
        default=1, description="Initial retry delay (seconds)"
    )

    CRAWLER_RETRY_MULTIPLIER: float = Field(
        default=2.0, description="Retry delay multiplier for exponential backoff"
    )

    CRAWLER_RETRY_MAX_DELAY: int = Field(
        default=10, description="Maximum retry delay (seconds)"
    )

    # Crawler Selection
    CRAWLER_DEFAULT_TYPE: Literal["playwright", "crawl4ai"] = Field(
        default="playwright", description="Default crawler implementation"
    )

    # Browser Configuration (Playwright)
    CRAWLER_BROWSER_HEADLESS: bool = Field(
        default=True, description="Run browser in headless mode"
    )

    CRAWLER_BROWSER_TIMEOUT: int = Field(
        default=30000, description="Browser operation timeout (milliseconds)"
    )

    CRAWLER_BROWSER_VIEWPORT_WIDTH: int = Field(
        default=1920, description="Browser viewport width"
    )

    CRAWLER_BROWSER_VIEWPORT_HEIGHT: int = Field(
        default=1080, description="Browser viewport height"
    )

    # Content Configuration
    CRAWLER_MAX_CONTENT_LENGTH: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum content length to fetch (bytes)",
    )

    CRAWLER_FOLLOW_REDIRECTS: bool = Field(
        default=True, description="Follow HTTP redirects"
    )

    CRAWLER_MAX_REDIRECTS: int = Field(
        default=5, description="Maximum number of redirects to follow"
    )

    # robots.txt Configuration
    CRAWLER_RESPECT_ROBOTS_TXT: bool = Field(
        default=True, description="Respect robots.txt rules"
    )

    CRAWLER_ROBOTS_CACHE_TTL: int = Field(
        default=3600, description="robots.txt cache TTL (seconds)"
    )

    # ==================== Future AI Providers ====================
    # Reserved for future milestones
    OPENAI_API_KEY: str | None = Field(
        default=None, description="OpenAI API key (future milestone)"
    )

    ANTHROPIC_API_KEY: str | None = Field(
        default=None, description="Anthropic API key (future milestone)"
    )

    # ==================== Validation ====================
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("PORT", "DATABASE_PORT", "REDIS_PORT")
    @classmethod
    def validate_ports(cls, v: int) -> int:
        """Validate port numbers are in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function is cached to avoid reloading settings on every call.
    Settings are loaded once and reused throughout the application.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Export for easy import
__all__ = ["Settings", "get_settings"]
