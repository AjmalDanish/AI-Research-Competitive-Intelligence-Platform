"""
Crawler Service

Main orchestrator for crawling operations following Clean Architecture.

Clean Architecture:
- Service layer
- Coordinates multiple components
- Depends on interfaces where possible
"""

import asyncio
from datetime import datetime, timezone
from typing import Literal

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.core.domain.crawler import CrawlResult, CrawlerConfig
from backend.crawler.implementations import PlaywrightCrawler, Crawl4AICrawler

logger = get_logger(__name__)
settings = get_settings()


class CrawlerService:
    """
    Main crawler service orchestrator.
    
    Coordinates the complete crawling pipeline:
    1. URL validation and normalization
    2. robots.txt checking
    3. Web page crawling
    4. Error handling and retry logic
    """
    
    def __init__(
        self,
        crawler_type: Literal["playwright", "crawl4ai"] = "playwright",
        config: CrawlerConfig | None = None,
    ):
        """
        Initialize crawler service.
        
        Args:
            crawler_type: Type of crawler to use (playwright/crawl4ai)
            config: Crawler configuration
        """
        self.config = config or CrawlerConfig.from_settings(settings)
        self.crawler_type = crawler_type
        self.crawler = self._create_crawler()
    
    def _create_crawler(self) -> "PlaywrightCrawler | Crawl4AICrawler":
        """Create crawler instance based on type."""
        if self.crawler_type == "playwright":
            return PlaywrightCrawler(config=self.config)
        elif self.crawler_type == "crawl4ai":
            return Crawl4AICrawler(config=self.config)
        else:
            logger.warning(f"Unknown crawler type: {self.crawler_type}, defaulting to playwright")
            return PlaywrightCrawler(config=self.config)
    
    async def crawl_url(
        self,
        url: str,
    ) -> CrawlResult:
        """
        Crawl a URL with full pipeline validation and checking.
        
        Args:
            url: URL to crawl
            
        Returns:
            CrawlResult with HTML content and metadata
        """
        logger.info(f"Crawling URL: {url}")
        
        try:
            # Crawl the URL (crawler handles validation internally)
            result = await self.crawler.crawl(url, config=self.config)
            
            logger.info(f"Crawl completed: {url} - success={result.is_success}, status={result.status_code}, length={result.content_length}, duration={result.metrics.duration_seconds if result.metrics else 0}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Crawl failed: {url} - {str(e)}")
            return CrawlResult.from_error(
                url=url,
                error=str(e),
                crawler_name=self.crawler_type,
            )
    
    async def crawl_multiple(
        self,
        urls: list[str],
        max_concurrent: int = 5,
    ) -> list[CrawlResult]:
        """
        Crawl multiple URLs concurrently.
        
        Args:
            urls: List of URLs to crawl
            max_concurrent: Maximum concurrent crawls
            
        Returns:
            List of CrawlResult objects
        """
        logger.info(f"Crawling {len(urls)} URLs concurrently (max: {max_concurrent})")
        
        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url: str) -> CrawlResult:
            """Crawl URL with semaphore limiting."""
            async with semaphore:
                return await self.crawler_url(url)
        
        # Crawl all URLs concurrently
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    CrawlResult.from_error(
                        url=urls[i],
                        error=str(result),
                        crawler_name=self.crawler_type,
                    )
                )
            else:
                final_results.append(result)
        
        successful = sum(1 for r in final_results if r.is_success)
        logger.info(
            f"Completed crawling {len(urls)} URLs",
            successful=successful,
            failed=len(final_results) - successful,
        )
        
        return final_results
    
    def switch_crawler(self, crawler_type: Literal["playwright", "crawl4ai"]) -> None:
        """Switch to a different crawler implementation."""
        logger.info(f"Switching crawler from {self.crawler_type} to {crawler_type}")
        self.crawler_type = crawler_type
        self.crawler = self._create_crawler()
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Clean up resources if needed
        pass


# Export for easy import
__all__ = ["CrawlerService"]