"""
Unit tests for the scraping service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.services.scraping_service import (
    ScrapingConfig,
    ScrapedData,
    HTMLScraper,
    ScrapingOrchestrator,
)


@pytest.fixture
def scraping_config():
    """Create a test scraping configuration."""
    return ScrapingConfig(
        max_concurrent_requests=2,
        request_timeout=10,
        retry_attempts=2,
        respect_robots_txt=True
    )


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta name="keywords" content="test, scraping, python">
    </head>
    <body>
        <h1>Main Heading</h1>
        <h2>Subheading</h2>
        <p>This is a test paragraph with some content.</p>
        <a href="https://example.com">Example Link</a>
        <a href="/internal">Internal Link</a>
    </body>
    </html>
    """


class TestScrapingConfig:
    """Tests for ScrapingConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ScrapingConfig()
        
        assert config.max_concurrent_requests == 5
        assert config.request_timeout == 30
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0
        assert config.respect_robots_txt is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = ScrapingConfig(
            max_concurrent_requests=10,
            request_timeout=60,
            retry_attempts=5,
            retry_delay=2.0
        )
        
        assert config.max_concurrent_requests == 10
        assert config.request_timeout == 60
        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0


class TestScrapedData:
    """Tests for ScrapedData dataclass."""
    
    def test_scraped_data_creation(self):
        """Test creating scraped data."""
        data = ScrapedData(
            url="https://example.com",
            title="Test Title",
            content="Test content",
            metadata={"key": "value"},
            scraped_at=datetime.utcnow(),
            source_type="html"
        )
        
        assert data.url == "https://example.com"
        assert data.title == "Test Title"
        assert data.content == "Test content"
        assert data.metadata == {"key": "value"}
        assert data.source_type == "html"
        assert data.raw_html is None
    
    def test_scraped_data_with_html(self):
        """Test scraped data with raw HTML."""
        data = ScrapedData(
            url="https://example.com",
            title="Test Title",
            content="Test content",
            metadata={},
            scraped_at=datetime.utcnow(),
            source_type="html",
            raw_html="<html><body>Test</body></html>"
        )
        
        assert data.raw_html == "<html><body>Test</body></html>"


class TestHTMLScraper:
    """Tests for HTMLScraper class."""
    
    @pytest.mark.asyncio
    async def test_extract_data_title(self, sample_html):
        """Test extracting title from HTML."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert data['title'] == 'Test Page'
    
    @pytest.mark.asyncio
    async def test_extract_data_meta(self, sample_html):
        """Test extracting meta tags from HTML."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert 'meta' in data
        assert data['meta']['description'] == 'Test description'
        assert data['meta']['keywords'] == 'test, scraping, python'
    
    @pytest.mark.asyncio
    async def test_extract_data_links(self, sample_html):
        """Test extracting links from HTML."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert 'links' in data
        assert len(data['links']) == 2
        assert data['links'][0]['url'] == 'https://example.com'
        assert data['links'][0]['text'] == 'Example Link'
    
    @pytest.mark.asyncio
    async def test_extract_data_headings(self, sample_html):
        """Test extracting headings from HTML."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert 'headings' in data
        assert 'h1' in data['headings']
        assert data['headings']['h1'] == ['Main Heading']
        assert data['headings']['h2'] == ['Subheading']
    
    @pytest.mark.asyncio
    async def test_extract_data_content(self, sample_html):
        """Test extracting main content from HTML."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert 'content' in data
        assert 'Test paragraph' in data['content']
    
    @pytest.mark.asyncio
    async def test_extract_data_word_count(self, sample_html):
        """Test word count calculation."""
        scraper = HTMLScraper(ScrapingConfig())
        data = scraper.extract_data(sample_html)
        
        assert 'word_count' in data
        assert data['word_count'] > 0


class TestScrapingOrchestrator:
    """Tests for ScrapingOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        config = ScrapingConfig()
        orchestrator = ScrapingOrchestrator(config)
        
        assert orchestrator.config == config
        assert 'html' in orchestrator.scrapers
        assert 'javascript' in orchestrator.scrapers
        assert 'api' in orchestrator.scrapers
    
    @pytest.mark.asyncio
    async def test_scrape_multiple_empty_list(self):
        """Test scraping empty URL list."""
        config = ScrapingConfig()
        orchestrator = ScrapingOrchestrator(config)
        
        results = await orchestrator.scrape_multiple([])
        
        assert results == []
    
    @pytest.mark.asyncio
    @patch('app.services.scraping_service.HTMLScraper')
    async def test_scrape_multiple_success(self, mock_scraper_class):
        """Test successful multiple scraping."""
        config = ScrapingConfig()
        orchestrator = ScrapingOrchestrator(config)
        
        # Mock scraper behavior
        mock_scraper = AsyncMock()
        mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
        mock_scraper.__aexit__ = AsyncMock()
        mock_scraper.scrape = AsyncMock()
        
        mock_scraper_class.return_value = mock_scraper
        
        urls = ["https://example1.com", "https://example2.com"]
        results = await orchestrator.scrape_multiple(urls, scraper_type='html')
        
        # Verify mock was called correctly
        assert mock_scraper.__aenter__.await_count == 2


@pytest.mark.integration
class TestScrapingIntegration:
    """Integration tests for scraping functionality."""
    
    @pytest.mark.asyncio
    async def test_full_scraping_workflow(self, sample_html):
        """Test complete scraping workflow."""
        config = ScrapingConfig(max_concurrent_requests=1, request_timeout=10)
        
        # Create scraper and extract data
        scraper = HTMLScraper(config)
        data = scraper.extract_data(sample_html)
        
        # Verify all expected fields are present
        required_fields = ['title', 'content', 'meta', 'links', 'headings', 'word_count']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify data quality
        assert len(data['title']) > 0
        assert len(data['content']) > 0
        assert data['word_count'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])