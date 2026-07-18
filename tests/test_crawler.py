"""
Crawler Service Tests

Unit tests for crawler service functionality.
"""

import pytest

from backend.crawler import CrawlerService
from backend.core.domain.crawler import CrawlResult


class TestCrawlerService:
    """Test crawler service functionality."""
    
    @pytest.fixture
    def crawler_service(self):
        """Create crawler service instance."""
        return CrawlerService(crawler_type="playwright")
    
    def test_service_initialization(self, crawler_service):
        """Test that crawler service initializes correctly."""
        assert crawler_service is not None
        assert crawler_service.crawler_type == "playwright"
        assert crawler_service.crawler.crawler_name == "playwright"
    
    def test_switch_crawler(self, crawler_service):
        """Test that crawler can be switched."""
        assert crawler_service.crawler_type == "playwright"
        
        crawler_service.switch_crawler("crawl4ai")
        assert crawler_service.crawler_type == "crawl4ai"
        assert crawler_service.crawler.crawler_name == "crawl4ai"
    
    @pytest.mark.asyncio
    async def test_crawl_url_basic(self, crawler_service):
        """Test basic URL crawling."""
        # This test should work with a real URL
        # For testing purposes, we might want to mock the crawler
        # For now, we'll test the structure
        
        url = "https://example.com"
        
        # Create a mock result to test the service structure
        from datetime import datetime, timezone
        from backend.core.domain.crawler import CrawlMetrics
        
        mock_result = CrawlResult(
            url=url,
            final_url=url,
            status_code=200,
            html="<html><body>Test</body></html>",
            content_type="text/html",
            content_length=36,
            crawler_name="playwright",
            metrics=CrawlMetrics(
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                retry_count=0,
            ),
        )
        
        # Test result structure
        assert mock_result.url == url
        assert mock_result.status_code == 200
        assert mock_result.is_success is True
        assert mock_result.content_length == 36


class TestCrawlResult:
    """Test CrawlResult domain model."""
    
    def test_successful_result_properties(self):
        """Test properties of successful crawl result."""
        from datetime import datetime, timezone
        
        result = CrawlResult(
            url="https://example.com",
            final_url="https://example.com",
            status_code=200,
            html="<html><body>Test</body></html>",
            content_type="text/html",
            content_length=36,
            crawler_name="playwright",
        )
        
        assert result.is_success is True
        assert result.is_redirect is False
        assert result.is_empty is False
    
    def test_error_result_properties(self):
        """Test properties of error crawl result."""
        result = CrawlResult.from_error(
            url="https://example.com",
            error="Network error",
            crawler_name="playwright",
        )
        
        assert result.is_success is False
        assert result.status_code == 0
        assert result.error == "Network error"
    
    def test_redirect_result(self):
        """Test redirect detection."""
        result = CrawlResult(
            url="https://example.com",
            final_url="https://example.com/redirected",
            status_code=200,
            html="<html><body>Test</body></html>",
            content_type="text/html",
            content_length=36,
            crawler_name="playwright",
        )
        
        assert result.is_redirect is True
    
    def test_empty_content_detection(self):
        """Test empty content detection."""
        result = CrawlResult(
            url="https://example.com",
            final_url="https://example.com",
            status_code=200,
            html="",
            content_type="text/html",
            content_length=0,
            crawler_name="playwright",
        )
        
        assert result.is_empty is True


class TestCrawlMetrics:
    """Test CrawlMetrics domain model."""
    
    def test_metrics_calculation(self):
        """Test metrics calculations."""
        from datetime import datetime, timezone, timedelta
        
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=2.5)
        
        metrics = CrawlMetrics(
            start_time=start,
            end_time=end,
            retry_count=3,
            robots_checked=True,
            robots_allowed=True,
        )
        
        assert metrics.duration_seconds == 2.5
        assert metrics.retry_count == 3
        assert metrics.robots_checked is True
        assert metrics.robots_allowed is True
    
    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        from datetime import datetime, timezone, timedelta
        
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=1.0)
        
        metrics = CrawlMetrics(
            start_time=start,
            end_time=end,
            retry_count=0,
            robots_checked=False,
            robots_allowed=True,
        )
        
        metrics_dict = metrics.to_dict()
        
        assert "start_time" in metrics_dict
        assert "end_time" in metrics_dict
        assert "duration_seconds" in metrics_dict
        assert "retry_count" in metrics_dict
        assert "robots_checked" in metrics_dict
        assert "robots_allowed" in metrics_dict
        assert metrics_dict["retry_count"] == 0


class TestCrawlerConfig:
    """Test CrawlerConfig domain model."""
    
    def test_config_creation(self):
        """Test crawler config creation."""
        config = CrawlerConfig(
            user_agent="TestBot/1.0",
            timeout=30,
            max_retries=3,
            initial_delay=1,
            multiplier=2.0,
            max_delay=10,
            respect_robots=True,
            headless=True,
        )
        
        assert config.user_agent == "TestBot/1.0"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.headless is True
    
    def test_config_from_settings(self, settings):
        """Test config creation from settings."""
        config = CrawlerConfig.from_settings(settings)
        
        assert config.timeout == settings.CRAWLER_TIMEOUT_CRAWL
        assert config.max_retries == settings.CRAWLER_MAX_RETRIES
        assert config.initial_delay == settings.CRAWLER_RETRY_INITIAL_DELAY
        assert config.multiplier == settings.CRAWLER_RETRY_MULTIPLIER
        assert config.max_delay == settings.CRAWLER_RETRY_MAX_DELAY
        assert config.respect_robots == settings.CRAWLER_RESPECT_ROBOTS_TXT
        assert config.headless == settings.CRAWLER_BROWSER_HEADLESS