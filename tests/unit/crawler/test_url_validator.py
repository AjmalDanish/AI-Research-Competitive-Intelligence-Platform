"""
URL Validator Tests

Unit tests for URL validation and normalization.
"""

import pytest

from backend.crawler.validators import URLValidator, URLNormalizer
from backend.crawler.exceptions import ValidationError


class TestURLValidator:
    """Test URL validation."""
    
    @pytest.fixture
    def validator(self):
        """Create URL validator instance."""
        return URLValidator(timeout=5, check_accessibility=False)
    
    def test_validate_valid_urls(self, validator):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com:8080/path",
        ]
        
        for url in valid_urls:
            assert validator.validate(url) is True
    
    def test_validate_empty_url(self, validator):
        """Test validation of empty URL."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("")
        assert "empty" in str(exc_info.value).lower()
    
    def test_validate_missing_scheme(self, validator):
        """Test validation of URL without scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("example.com")
        assert "scheme" in str(exc_info.value).lower()
    
    def test_validate_invalid_scheme(self, validator):
        """Test validation of URL with invalid scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("ftp://example.com")
        assert "scheme" in str(exc_info.value).lower()
    
    def test_normalize_urls(self, validator):
        """Test URL normalization."""
        test_cases = [
            ("HTTP://EXAMPLE.COM", "http://example.com"),
            ("https://WWW.EXAMPLE.COM", "https://example.com"),
            ("https://example.com:443/path", "https://example.com/path"),
            ("https://example.com:80/path", "https://example.com/path"),
        ]
        
        for input_url, expected in test_cases:
            result = validator.normalize(input_url)
            assert result == expected, f"Expected {expected}, got {result}"
    
    def test_extract_domain(self, validator):
        """Test domain extraction."""
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("http://example.com:8080/path", "example.com:8080"),
            ("https://sub.example.com/path", "sub.example.com"),
        ]
        
        for url, expected in test_cases:
            result = validator.extract_domain(url)
            assert result == expected, f"Expected {expected}, got {result}"


class TestURLNormalizer:
    """Test URL normalization."""
    
    def test_normalize_basic_urls(self):
        """Test basic URL normalization."""
        test_cases = [
            ("https://example.com", "https://example.com"),
            ("HTTPS://EXAMPLE.COM", "https://example.com"),
            ("https://example.com/", "https://example.com"),
            ("https://example.com/path/", "https://example.com/path"),
        ]
        
        for input_url, expected in test_cases:
            result = URLNormalizer.normalize(input_url)
            assert result == expected, f"Expected {expected}, got {result}"
    
    def test_normalize_remove_www(self):
        """Test removing www prefix."""
        test_cases = [
            ("https://www.example.com", "https://example.com"),
            ("https://WWW.EXAMPLE.COM", "https://example.com"),
        ]
        
        for input_url, expected in test_cases:
            result = URLNormalizer.normalize(input_url, remove_www=True)
            assert result == expected, f"Expected {expected}, got {result}"
    
    def test_normalize_remove_default_ports(self):
        """Test removing default ports."""
        test_cases = [
            ("https://example.com:443", "https://example.com"),
            ("http://example.com:80", "http://example.com"),
            ("https://example.com:8080", "https://example.com:8080"),
        ]
        
        for input_url, expected in test_cases:
            result = URLNormalizer.normalize(input_url)
            assert result == expected, f"Expected {expected}, got {result}"
    
    def test_normalize_relative_urls(self):
        """Test resolving relative URLs."""
        test_cases = [
            ("/path", "https://example.com/path"),
            ("../path", "https://example.com/../path"),
        ]
        
        for relative, expected in test_cases:
            result = URLNormalizer.make_absolute(relative, "https://example.com/")
            assert expected in result, f"Expected {expected} in {result}"
    
    def test_are_equivalent(self):
        """Test URL equivalence checking."""
        equivalent_pairs = [
            ("https://example.com", "https://example.com/"),
            ("https://EXAMPLE.COM", "https://example.com"),
            ("https://www.example.com", "https://example.com"),
            ("https://example.com:443", "https://example.com"),
        ]
        
        for url1, url2 in equivalent_pairs:
            assert URLNormalizer.are_equivalent(url1, url2), f"URLs should be equivalent: {url1} == {url2}"
    
    def test_normalize_list(self):
        """Test normalizing a list of URLs."""
        urls = [
            "https://example.com",
            "https://example.com/",
            "HTTPS://EXAMPLE.COM",
            "https://www.example.com",
        ]
        
        normalized = URLNormalizer.normalize_list(urls, remove_duplicates=True)
        
        # After normalization and deduplication, should have only 1 unique URL
        assert len(normalized) == 1
        assert normalized[0] == "https://example.com"