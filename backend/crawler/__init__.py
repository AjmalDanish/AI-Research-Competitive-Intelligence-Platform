"""
Crawler Module

Web crawling functionality following Clean Architecture.

This module contains the complete crawling pipeline:

- crawler_service: Main orchestrator for crawling operations
- implementations: Playwright and Crawl4AI crawler implementations

Clean Architecture:
- Infrastructure layer
- Orchestrates web crawling
- Implements ICrawler interface
"""

from backend.core.domain.crawler import CrawlerConfig, CrawlMetrics, CrawlResult
from backend.core.interfaces.crawler import ICrawler
from backend.crawler.crawler_service import CrawlerService
from backend.crawler.implementations import Crawl4AICrawler, PlaywrightCrawler

# Export for easy import
__all__ = [
    # Main service
    "CrawlerService",
    # Crawler implementations
    "PlaywrightCrawler",
    "Crawl4AICrawler",
    # Core domain models
    "CrawlResult",
    "CrawlMetrics",
    "CrawlerConfig",
    # Core interface
    "ICrawler",
]
