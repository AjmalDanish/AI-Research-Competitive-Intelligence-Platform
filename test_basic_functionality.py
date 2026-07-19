"""
Simple synchronous tests to verify core functionality.
"""

import pytest
from backend.core.domain.crawler import (
    CrawlerConfig,
    CrawlMetrics,
    CrawlResult,
)
from backend.crawler.validators.url_validator import URLValidator


def test_crawl_config_creation():
    """Test that CrawlerConfig can be created."""
    config = CrawlerConfig(
        user_agent="TestAgent/1.0",
        timeout=10,
        headless=True,
    )
    assert config.user_agent == "TestAgent/1.0"
    assert config.timeout == 10
    assert config.headless is True


def test_crawl_result_creation():
    """Test that CrawlResult can be created."""
    result = CrawlResult(
        url="https://example.com",
        success=True,
        html_content="<html></html>",
        status_code=200,
        metrics=CrawlMetrics(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:00:01",
            duration_ms=1000,
            bytes_transferred=1024,
            num_retries=0,
            final_status="success",
        ),
    )
    assert result.url == "https://example.com"
    assert result.success is True
    assert result.status_code == 200


def test_url_validator_basic():
    """Test basic URL validation."""
    validator = URLValidator(check_accessibility_enabled=False)

    # Test valid URL
    assert validator.is_valid_url("https://example.com") is True
    assert validator.is_valid_url("http://example.com/path") is True

    # Test invalid URL
    assert validator.is_valid_url("not-a-url") is False
    assert validator.is_valid_url("") is False
    assert validator.is_valid_url("ftp://example.com") is False


def test_url_normalization():
    """Test URL normalization."""
    validator = URLValidator(check_accessibility_enabled=False)

    # Test basic normalization
    assert validator.normalize("HTTPS://EXAMPLE.COM/") == "https://example.com/"
    assert validator.normalize("http://example.com:80/") == "http://example.com/"

    # Test path normalization
    assert (
        validator.normalize("https://example.com/path/./../path/")
        == "https://example.com/path/"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
