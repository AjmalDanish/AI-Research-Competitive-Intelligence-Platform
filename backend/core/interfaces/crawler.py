"""
Crawler Interface

Core interface for crawler implementations.

Clean Architecture:
- Core layer (interfaces)
- No implementation details
- Pure interface definition
"""

from typing import Protocol

from backend.core.domain.crawler import CrawlerConfig, CrawlResult


class ICrawler(Protocol):
    """
    Abstract crawler interface for all crawler implementations.
    
    This interface defines the contract that all crawlers must implement.
    It enables dependency inversion and makes crawlers interchangeable.
    """

    async def crawl(
        self,
        url: str,
        config: CrawlerConfig | None = None,
    ) -> CrawlResult:
        """
        Crawl a URL and return raw HTML content.
        
        Args:
            url: The URL to crawl
            config: Crawler configuration (optional, uses defaults if None)
            
        Returns:
            CrawlResult containing the HTML content and metadata
            
        Raises:
            CrawlerException: If crawling fails and retries are exhausted
            ValidationError: If URL is invalid
            RobotsDeniedException: If robots.txt denies access
        """
        ...

    @property
    def crawler_name(self) -> str:
        """
        Get the name of the crawler implementation.
        
        Returns:
            Name identifying this crawler implementation
        """
        ...


# Export for easy import
__all__ = ["ICrawler"]
