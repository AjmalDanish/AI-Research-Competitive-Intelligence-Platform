"""
Crawler Domain Module

Domain entities for the crawler module.

Clean Architecture:
- Core layer (domain)
- Pure business logic
- Framework-independent
"""

from datetime import datetime, timezone


class CrawlMetrics:
    """
    Crawl execution metrics.
    
    Lightweight metrics as approved for MVP.
    """
    
    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        retry_count: int = 0,
        robots_checked: bool = False,
        robots_allowed: bool = True,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.retry_count = retry_count
        self.robots_checked = robots_checked
        self.robots_allowed = robots_allowed
    
    @property
    def duration_seconds(self) -> float:
        """Calculate crawl duration in seconds."""
        delta = self.end_time - self.start_time
        return delta.total_seconds()
    
    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "retry_count": self.retry_count,
            "robots_checked": self.robots_checked,
            "robots_allowed": self.robots_allowed,
        }


class CrawlResult:
    """
    Result of a crawl operation.
    
    Contains the raw HTML content and metadata from a successful crawl.
    """
    
    def __init__(
        self,
        url: str,
        final_url: str,
        status_code: int,
        html: str,
        content_type: str | None = None,
        content_length: int | None = None,
        crawler_name: str = "playwright",
        metrics: CrawlMetrics | None = None,
        crawled_at: datetime | None = None,
        error: str | None = None,
    ):
        self.url = url
        self.final_url = final_url
        self.status_code = status_code
        self.html = html
        self.content_type = content_type
        self.content_length = content_length
        self.crawler_name = crawler_name
        self.metrics = metrics
        self.crawled_at = crawled_at or datetime.now(timezone.utc)
        self.error = error
    
    @property
    def is_success(self) -> bool:
        """Check if crawl was successful."""
        return self.status_code >= 200 and self.status_code < 300 and self.error is None
    
    @property
    def is_redirect(self) -> bool:
        """Check if result involved redirect."""
        return self.url != self.final_url
    
    @property
    def is_empty(self) -> bool:
        """Check if content is empty."""
        return not self.html or len(self.html.strip()) == 0
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "url": self.url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "html": self.html,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "crawler_name": self.crawler_name,
            "crawled_at": self.crawled_at.isoformat(),
            "error": self.error,
            "is_success": self.is_success,
            "is_redirect": self.is_redirect,
            "is_empty": self.is_empty,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }
    
    @classmethod
    def from_error(
        cls,
        url: str,
        error: str,
        status_code: int = 0,
        crawler_name: str = "playwright",
    ) -> "CrawlResult":
        """Create a crawl result representing an error."""
        return cls(
            url=url,
            final_url=url,
            status_code=status_code,
            html="",
            content_type=None,
            content_length=0,
            crawler_name=crawler_name,
            crawled_at=datetime.now(timezone.utc),
            error=error,
        )


class CrawlerConfig:
    """
    Configuration for crawler operations.
    
    Runtime configuration for crawl operations,
    separate from application settings.
    """
    
    def __init__(
        self,
        user_agent: str,
        timeout: int = 30,
        max_retries: int = 3,
        initial_delay: int = 1,
        multiplier: float = 2.0,
        max_delay: int = 10,
        respect_robots: bool = True,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        max_content_length: int = 10 * 1024 * 1024,
        headless: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.respect_robots = respect_robots
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.max_content_length = max_content_length
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
    
    @classmethod
    def from_settings(cls, settings) -> "CrawlerConfig":
        """Create crawler config from application settings."""
        return cls(
            user_agent=settings.CRAWLER_USER_AGENT,
            timeout=settings.CRAWLER_TIMEOUT_CRAWL,
            max_retries=settings.CRAWLER_MAX_RETRIES,
            initial_delay=settings.CRAWLER_RETRY_INITIAL_DELAY,
            multiplier=settings.CRAWLER_RETRY_MULTIPLIER,
            max_delay=settings.CRAWLER_RETRY_MAX_DELAY,
            respect_robots=settings.CRAWLER_RESPECT_ROBOTS_TXT,
            follow_redirects=settings.CRAWLER_FOLLOW_REDIRECTS,
            max_redirects=settings.CRAWLER_MAX_REDIRECTS,
            max_content_length=settings.CRAWLER_MAX_CONTENT_LENGTH,
            headless=settings.CRAWLER_BROWSER_HEADLESS,
            viewport_width=settings.CRAWLER_BROWSER_VIEWPORT_WIDTH,
            viewport_height=settings.CRAWLER_BROWSER_VIEWPORT_HEIGHT,
        )


# Export for easy import
__all__ = [
    "CrawlMetrics",
    "CrawlResult",
    "CrawlerConfig",
]