"""
Playwright Crawler

Primary crawler implementation using Playwright.

Clean Architecture:
- Infrastructure layer
- Implements ICrawler interface
- Playwright-specific implementation
"""

from datetime import UTC, datetime

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.core.domain.crawler import CrawlerConfig, CrawlMetrics, CrawlResult
from backend.core.interfaces.crawler import ICrawler
from backend.crawler.exceptions import (
    ContentLengthException,
)
from typing import Any, Optional
from playwright.async_api import Page, async_playwright, Browser, Playwright

logger = get_logger(__name__)
settings = get_settings()


class PlaywrightCrawler(ICrawler):
    """
    Playwright-based crawler implementation.

    Primary crawler using Chromium in headless mode.
    """

    def __init__(self, config: CrawlerConfig | None = None):
        """Initialize Playwright crawler."""
        self.config = config or CrawlerConfig.from_settings(settings)
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[Any] = None

    @property
    def crawler_name(self) -> str:
        """Get the name of this crawler implementation."""
        return "playwright"

    async def _init_browser(self) -> None:
        """Initialize Playwright browser."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()

        if self._browser is None:
            self._browser = await self._playwright.chromium.launch(
                headless=self.config.headless,
            )

        if self._context is None:
            self._context = await self._browser.new_context(
                user_agent=self.config.user_agent,
                viewport={
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                },
            )

    async def _close_browser(self) -> None:
        """Close Playwright browser."""
        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def crawl(
        self,
        url: str,
        config: CrawlerConfig | None = None,
    ) -> CrawlResult:
        """
        Crawl a URL using Playwright.

        Args:
            url: URL to crawl
            config: Crawler configuration (optional)

        Returns:
            CrawlResult with HTML content and metadata
        """
        crawl_config = config or self.config
        start_time = datetime.now(UTC)

        try:
            await self._init_browser()

            if self._context is None:
                raise RuntimeError("Browser context not initialized")

            page: Page = await self._context.new_page()

            try:
                # Set timeout
                timeout = crawl_config.timeout * 1000  # Convert to ms

                # Navigate to URL
                response = await page.goto(
                    url,
                    timeout=timeout,
                    wait_until="domcontentloaded",
                )

                # Get final URL (after redirects)
                final_url = page.url

                # Get status code
                status_code = response.status if response else 0

                # Get HTML content
                html = await page.content()
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
                if response:
                    headers = response.headers or {}
                    content_type = headers.get("content-type", "")

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

            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Playwright crawl failed: {url} - {str(e)}")
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
        finally:
            await self._close_browser()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self._close_browser()


# Export for easy import
__all__ = ["PlaywrightCrawler"]
