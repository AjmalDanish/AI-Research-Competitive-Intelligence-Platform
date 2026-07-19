"""
Web scraping service for competitive intelligence data collection.

This module provides comprehensive web scraping capabilities with support for
multiple data sources, rate limiting, and data extraction.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapingConfig:
    """Configuration for scraping operations."""

    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    respect_robots_txt: bool = True
    user_agent: str = settings.USER_AGENT
    rate_limit_delay: float = 2.0


@dataclass
class ScrapedData:
    """Container for scraped data."""

    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    scraped_at: datetime
    source_type: str
    raw_html: Optional[str] = None


class BaseScraper(ABC):
    """Abstract base class for web scrapers."""

    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logger

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
            headers={"User-Agent": self.config.user_agent},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def scrape(self, url: str) -> ScrapedData:
        """Scrape data from a URL."""
        pass

    @abstractmethod
    def extract_data(self, html: str) -> Dict[str, Any]:
        """Extract structured data from HTML."""
        pass


class HTMLScraper(BaseScraper):
    """HTML-based web scraper using BeautifulSoup."""

    async def scrape(self, url: str) -> ScrapedData:
        """
        Scrape HTML content from a URL.

        Args:
            url: URL to scrape

        Returns:
            ScrapedData: Extracted data
        """
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

                self.logger.info(f"Successfully scraped {url}")

                # Extract structured data
                data = self.extract_data(html)

                return ScrapedData(
                    url=url,
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    metadata=data,
                    scraped_at=datetime.utcnow(),
                    source_type="html",
                    raw_html=html,
                )

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            raise

    def extract_data(self, html: str) -> Dict[str, Any]:
        """
        Extract structured data from HTML.

        Args:
            html: HTML content

        Returns:
            Dict containing extracted data
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string.strip()

        # Extract meta tags
        meta_data = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                meta_data[name] = content

        # Extract main content
        content = ""
        for tag in ["article", "main", "div"]:
            element = soup.find(tag)
            if element:
                content = element.get_text(strip=True)
                break

        # Extract links
        links = []
        for link in soup.find_all("a", href=True):
            links.append({"url": link["href"], "text": link.get_text(strip=True)})

        # Extract headings
        headings = {}
        for level in range(1, 7):
            headings[f"h{level}"] = [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]

        return {
            "title": title,
            "content": content,
            "meta": meta_data,
            "links": links,
            "headings": headings,
            "word_count": len(content.split()),
        }


class JavaScriptScraper(BaseScraper):
    """JavaScript-rendered content scraper using Selenium."""

    def __init__(self, config: ScrapingConfig):
        super().__init__(config)
        self.driver: Optional[webdriver.Chrome] = None

    async def __aenter__(self):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.config.user_agent}")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
        if self.session:
            await self.session.close()

    async def scrape(self, url: str) -> ScrapedData:
        """
        Scrape JavaScript-rendered content.

        Args:
            url: URL to scrape

        Returns:
            ScrapedData: Extracted data
        """
        try:
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get page HTML
            html = self.driver.page_source

            self.logger.info(f"Successfully scraped JS content from {url}")

            # Extract structured data
            data = self.extract_data(html)

            return ScrapedData(
                url=url,
                title=data.get("title", ""),
                content=data.get("content", ""),
                metadata=data,
                scraped_at=datetime.utcnow(),
                source_type="javascript",
                raw_html=html,
            )

        except Exception as e:
            self.logger.error(f"Error scraping JS content from {url}: {e}")
            raise

    def extract_data(self, html: str) -> Dict[str, Any]:
        """Extract structured data using BeautifulSoup."""
        soup = BeautifulSoup(html, "html.parser")

        return {
            "title": soup.title.string.strip() if soup.title else "",
            "content": soup.get_text(strip=True),
            "url": self.driver.current_url,
            "page_title": self.driver.title,
        }


class APIScraper(BaseScraper):
    """API endpoint scraper for JSON/XML data."""

    async def scrape(self, url: str, params: Optional[Dict] = None) -> ScrapedData:
        """
        Scrape data from API endpoint.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            ScrapedData: Extracted data
        """
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")

                if "application/json" in content_type:
                    data = await response.json()
                elif "application/xml" in content_type:
                    data = await response.text()
                else:
                    data = await response.text()

                self.logger.info(f"Successfully scraped API {url}")

                return ScrapedData(
                    url=url,
                    title=f"API Data: {url}",
                    content=str(data),
                    metadata={
                        "content_type": content_type,
                        "status_code": response.status,
                        "response_headers": dict(response.headers),
                    },
                    scraped_at=datetime.utcnow(),
                    source_type="api",
                )

        except Exception as e:
            self.logger.error(f"Error scraping API {url}: {e}")
            raise

    def extract_data(self, html: str) -> Dict[str, Any]:
        """Not used for API scraper."""
        return {}


class ScrapingOrchestrator:
    """Orchestrates multiple scraping operations."""

    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.logger = logger
        self.scrapers = {"html": HTMLScraper, "javascript": JavaScriptScraper, "api": APIScraper}

    async def scrape_multiple(
        self, urls: List[str], scraper_type: str = "html"
    ) -> List[ScrapedData]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            scraper_type: Type of scraper to use

        Returns:
            List of scraped data
        """
        scraper_class = self.scrapers.get(scraper_type, HTMLScraper)

        async with scraper_class(self.config) as scraper:
            tasks = [scraper.scrape(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and log them
            successful_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Scraping failed: {result}")
                else:
                    successful_results.append(result)

            self.logger.info(f"Scraped {len(successful_results)}/{len(urls)} URLs successfully")

            return successful_results

    async def scrape_with_retry(
        self, url: str, scraper_type: str = "html"
    ) -> Optional[ScrapedData]:
        """
        Scrape with retry logic.

        Args:
            url: URL to scrape
            scraper_type: Type of scraper to use

        Returns:
            ScrapedData or None if all retries fail
        """
        scraper_class = self.scrapers.get(scraper_type, HTMLScraper)

        for attempt in range(self.config.retry_attempts):
            try:
                async with scraper_class(self.config) as scraper:
                    return await scraper.scrape(url)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    self.logger.error(f"All retries failed for {url}")
                    return None


# Factory function for creating scrapers
def create_scraper(scraper_type: str, config: Optional[ScrapingConfig] = None) -> BaseScraper:
    """
    Create a scraper instance.

    Args:
        scraper_type: Type of scraper to create
        config: Scraping configuration

    Returns:
        Scraper instance
    """
    if config is None:
        config = ScrapingConfig()

    scrapers = {"html": HTMLScraper, "javascript": JavaScriptScraper, "api": APIScraper}

    scraper_class = scrapers.get(scraper_type, HTMLScraper)
    return scraper_class(config)
