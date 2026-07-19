"""
Crawl4AI Crawler

Secondary crawler implementation using Crawl4AI.

Clean Architecture:
- Infrastructure layer
- Implements ICrawler interface
- Crawl4AI-specific implementation
"""

from datetime import UTC, datetime

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.core.domain.crawler import CrawlerConfig, CrawlMetrics, CrawlResult
from backend.core.interfaces.crawler import ICrawler
from backend.crawler.exceptions import (
    ContentLengthException,
)

logger = get_logger(__name__)
settings = get_settings()


class Crawl4AICrawler(ICrawler):
    """
    Crawl4AI-based crawler implementation.

    Secondary crawler demonstrating interface polymorphism.
    """

    def __init__(self, config: CrawlerConfig | None = None):
        """Initialize Crawl4AI crawler."""
        self.config = config or CrawlerConfig.from_settings(settings)

    @property
    def crawler_name(self) -> str:
        """Get the name of this crawler implementation."""
        return "crawl4ai"

    async def crawl(
        self,
        url: str,
        config: CrawlerConfig | None = None,
    ) -> CrawlResult:
        """
        Crawl a URL using Crawl4AI.

        Args:
            url: URL to crawl
            config: Crawler configuration (optional)

        Returns:
            CrawlResult with HTML content and metadata
        """
        if AsyncWebCrawler is None:
            error_msg = "Crawl4AI is not installed"
            logger.error(error_msg)
            return CrawlResult.from_error(
                url=url,
                error=error_msg,
                crawler_name=self.crawler_name,
            )

        crawl_config = config or self.config
        start_time = datetime.now(UTC)

        try:
            async with AsyncWebCrawler(
                headless=crawl_config.headless,
                browser_type="chromium",
                user_agent=crawl_config.user_agent,
                verbose=False,
            ) as crawler:
                result = await crawler.arun(
                    url=url,
                    timeout=crawl_config.timeout * 1000,
                )

                # Get final URL
                final_url = result.url if result.url else url

                # Get status code
                status_code = result.status_code if hasattr(result, "status_code") else 200

                # Get HTML content
                html = result.html if result.html else ""
                content_length = len(html)

                # Check content length
                if content_length > crawl_config.max_content_length:
                    raise ContentLengthException(
                        "Content exceeds maximum length",
                        url=url,
                        content_length=content_length,
                        max_length=crawl_config.max_content_length,
                    )

                # Get content type
                content_type = None
                if hasattr(result, "response") and result.response:
                    content_type = result.response.headers.get("content-type", "")

                # Create metrics
                end_time = datetime.now(UTC)
                metrics = CrawlMetrics(
                    start_time=start_time,
                    end_time=end_time,
                    retry_count=0,
                    robots_checked=False,
                    robots_allowed=True,
                )

                return CrawlResult(
                    url=url,
                    final_url=final_url,
                    status_code=status_code,
                    html=html,
                    content_type=content_type,
                    content_length=content_length,
                    crawler_name=self.crawler_name,
                    metrics=metrics,
                )

        except Exception as e:
            logger.error(f"Crawl4AI crawl failed: {url}", error=str(e))
            end_time = datetime.now(UTC)
            metrics = CrawlMetrics(
                start_time=start_time,
                end_time=end_time,
                retry_count=0,
                robots_checked=False,
                robots_allowed=False,
            )
            return CrawlResult.from_error(
                url=url,
                error=str(e),
                crawler_name=self.crawler_name,
            )

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass  # Crawl4AI handles cleanup internally


# Export for easy import
__all__ = ["Crawl4AICrawler"]
