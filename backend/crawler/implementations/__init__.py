"""
Crawler Implementations

Crawler implementations following Clean Architecture.

This module contains:
- PlaywrightCrawler: Primary Playwright-based crawler
- Crawl4AICrawler: Secondary Crawl4AI-based crawler

Clean Architecture:
- Infrastructure layer
- Implements ICrawler interface
- Concrete crawler implementations
"""

from backend.crawler.implementations.crawl4ai_crawler import Crawl4AICrawler
from backend.crawler.implementations.playwright_crawler import PlaywrightCrawler

# Export for easy import
__all__ = [
    "PlaywrightCrawler",
    "Crawl4AICrawler",
]
