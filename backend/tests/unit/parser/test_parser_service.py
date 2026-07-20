"""
Unit tests for ParserService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List

from backend.parser.parser_service import ParserService, parser_service, get_parser_service
from backend.parser.exceptions import ParserNotFoundException


class TestParserServiceInitialization:
    """Test ParserService initialization."""
    
    def test_service_initialization_default(self):
        """Test service initialization with default parser."""
        service = ParserService()
        
        assert service.default_parser == "beautifulsoup"
        assert "beautifulsoup" in service.parsers
        assert "trafilatura" in service.parsers
    
    def test_service_initialization_custom_default(self):
        """Test service initialization with custom default parser."""
        service = ParserService(default_parser="trafilatura")
        
        assert service.default_parser == "trafilatura"
        assert service.parsers["trafilatura"] is not None
    
    def test_service_invalid_default_parser(self):
        """Test service with invalid default parser falls back to beautifulsoup."""
        service = ParserService(default_parser="invalid")
        
        # Should fall back to beautifulsoup
        assert service.default_parser == "beautifulsoup"
    
    def test_available_parsers(self):
        """Test getting available parsers."""
        service = ParserService()
        parsers = service.get_available_parsers()
        
        assert len(parsers) == 2
        assert "beautifulsoup" in parsers
        assert "trafilatura" in parsers


class TestParserServiceBasicParsing:
    """Test basic parsing operations."""
    
    @pytest.mark.asyncio
    async def test_parse_with_beautifulsoup(self):
        """Test parsing with BeautifulSoup parser."""
        service = ParserService()
        html = "<html><head><title>Test Page</title></head><body>Content</body></html>"
        
        result = await service.parse(html, "https://example.com", "beautifulsoup")
        
        assert result.success is True
        assert result.url == "https://examples.com"
        assert result.title == "Test Page"
    
    @pytest.mark.asyncio
    async def test_parse_with_trafilatura(self):
        """Test parsing with Trafilatura parser."""
        service = ParserService()
        html = "<html><head><title>Test Page</title></head><body>Content</body></html>"
        
        result = await service.parse(html, "https://example.com", "trafilatura")
        
        # Trafilatura should parse successfully
        assert result.url == "https://example.com"
        # Trafilatura might extract different content structure
    
    @pytest.mark.asyncio
    async def test_parse_with_default_parser(self):
        """Test parsing with default parser."""
        service = ParserService()
        html = "<html><head><title>Test Page</title></head><body>Content</body></html>"
        
        result = await service.parse(html, "https://example.com")
        
        assert result.success is True
        assert result.url == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_parse_empty_content(self):
        """Test parsing empty content."""
        service = ParserService()
        
        result = await service.parse("", "https://example.com")
        
        assert result.success is False
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_parse_with_options(self):
        """Test parsing with options."""
        service = ParserService()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        options = {"custom_option": "value"}
        
        result = await service.parse(html, "https://example.com", options=options)
        
        assert result.success is True


class TestParserServiceFallback:
    """Test fallback parsing mechanisms."""
    
    @pytest.mark.asyncio
    async def test_parse_with_fallback_success(self):
        """Test parse_with_fallback when first parser succeeds."""
        service = ParserService()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        
        result = await service.parse_with_fallback(
            html,
            "https://example.com",
            preferred_parser="beautifulsoup",
            fallback_parser="trafilatura"
        )
        
        assert result.success is True
        assert result.url == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_parse_with_fallback_first_fails(self):
        """Test parse_with_fallback when first parser fails."""
        service = ParserService()
        # Content that might cause issues (empty)
        html = ""
        
        result = await service.parse_with_fallback(
            html,
            "https://example.com",
            preferred_parser="beautifulsoup",
            fallback_parser="trafilatura"
        )
        
        # Both parsers should fail for empty content
        assert result.success is False
        assert result.error is not None


class TestParserServiceCapabilities:
    """Test parser capabilities queries."""
    
    def test_can_parse_with_default(self):
        """Test can_parse with default parser."""
        service = ParserService()
        html = "<html><body>Content</body></html>"
        
        can_parse = service.can_parse(html)
        
        assert can_parse is True
    
    def test_can_parse_empty(self):
        """Test can_parse with empty content."""
        service = ParserService()
        
        can_parse = service.can_parse("")
        
        assert can_parse is False
    
    def test_get_available_parsers(self):
        """Test getting available parsers."""
        service = ParserService()
        parsers = service.get_available_parsers()
        
        assert len(parsers) == 2
        assert "beautifulsoup" in parsers
        assert "trafilatura" in parsers
    
    def test_get_parser_capabilities_beautifulsoup(self):
        """Test getting BeautifulSoup capabilities."""
        service = ParserService()
        capabilities = service.get_parser_capabilities("beautifulsoup")
        
        assert capabilities["available"] is True
        assert capabilities["name"] == "beautifulsoup"
        assert len(capabilities["features"]) > 0
        assert "dom_traversal" in capabilities["features"]
        assert "link_extraction" in capabilities["features"]
    
    def test_get_parser_capabilities_trafilatura(self):
        """Test getting Trafilatura capabilities."""
        service = ParserService()
        capabilities = service.get_parser_capabilities("trafilatura")
        
        assert capabilities["available"] is True
        assert capabilities["name"] == "trafilatura"
        assert len(capabilities["features"]) > 0
        assert "text_extraction" in capabilities["features"]
        assert "content_cleaning" in capabilities["features"]
    
    def test_get_parser_capabilities_invalid(self):
        """Test getting capabilities for invalid parser."""
        service = ParserService()
        capabilities = service.get_parser_capabilities("invalid")
        
        assert capabilities["available"] is False
        assert len(capabilities["features"]) == 0
    
    def test_recommend_parser_no_requirements(self):
        """Test parser recommendation with no requirements."""
        service = ParserService()
        html = "<html><body>Content</body></html>"
        
        recommended = service.recommend_parser(html)
        
        # Should default to BeautifulSoup
        assert recommended in ["beautifulsoup", "trafilatura"]
    
    def test_recommend_parser_dom_requirements(self):
        """Test parser recommendation with DOM requirements."""
        service = ParserService()
        html = "<html><body>Content</body></html>"
        requirements = ["dom_traversal", "link_extraction"]
        
        recommended = service.recommend_parser(html, requirements)
        
        # Should recommend BeautifulSoup for DOM features
        assert recommended == "beautifulsoup"
    
    def test_recommend_parser_text_requirements(self):
        """Test parser recommendation with text requirements."""
        service = ParserService()
        html = "<html><body>Content</body></html>"
        requirements = ["text_extraction", "content_cleaning"]
        
        recommended = service.recommend_parser(html, requirements)
        
        # Should recommend Trafilatura for text features
        assert recommended == "trafilatura"


class TestParserServiceBatch:
    """Test batch parsing operations."""
    
    @pytest.mark.asyncio
    async def test_batch_parse_multiple_urls(self):
        """Test parsing multiple URLs."""
        service = ParserService()
        
        html_contents = [
            ("<html><head><title>Page 1</title></head><body>Content 1</body></html>", "https://example.com/page1"),
            ("<html><head><title>Page 2</title></head><body>Content 2</body></html>", "https://example.com/page2"),
            ("<html><head><title>Page 3</title></head><body>Content 3</body></html>", "https://example.com/page3"),
        ]
        
        results = await service.batch_parse(html_contents)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert results[0].title == "Page 1"
        assert results[1].title == "Page 2"
        assert results[2].title == "Page 3"
    
    @pytest.mark.asyncio
    async def test_batch_parse_with_failures(self):
        """Test batch parsing with some failures."""
        service = ParserService()
        
        html_contents = [
            ("<html><head><title>Good</title></head><body>Content</body></html>", "https://example.com/good"),
            ("", "https://example.com/bad"),  # Empty content
            ("<html><head><title>Good 2</title></head><body>Content</body></html>", "https://example.com/good2"),
        ]
        
        results = await service.batch_parse(html_contents)
        
        assert len(results) == 4
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True
    
    @pytest.mark.asyncio
    async def test_batch_parse_empty_list(self):
        """Test batch parsing with empty list."""
        service = ParserService()
        
        results = await service.batch_parse([])
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_batch_parse_with_specific_parser(self):
        """Test batch parsing with specific parser."""
        service = ParserService()
        
        html_contents = [
            ("<html><head><title>Page 1</title></head><body>Content 1</body></html>", "https://example.com/page1"),
            ("<html><head><title>Page 2</title></head><body>Content 2</body></html>", "https://example.com/page2"),
        ]
        
        results = await service.batch_parse(html_contents, parser_type="beautifulsoup")
        
        assert len(results) == 2
        assert all(r.success for r in results)
        assert all(r.metrics.parser_type == "beautifulsoup" for r in results if r.metrics)


class TestParserServiceMetrics:
    """Test parsing metrics."""
    
    @pytest.mark.asyncio
    async def test_metrics_in_result(self):
        """Test that metrics are included in result."""
        service = ParserService()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        
        result = await service.parse(html, "https://example.com")
        
        assert result.metrics is not None
        assert result.metrics.parser_type == "beautifulsoup"
        assert result.metrics.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_metrics_bytes_processed(self):
        """Test that bytes processed is calculated."""
        service = ParserService()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        
        result = await service.parse(html, "https://example.com")
        
        assert result.metrics is not None
        assert result.metrics.bytes_processed == len(html.encode("utf-8"))
    
    @pytest.mark.asyncio
    async def test_metrics_elements_extracted(self):
        """Test that elements extracted is calculated."""
        service = ParserService()
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main</h1>
            <p>Content</p>
            <a href="/link">Link</a>
            <img src="/image.jpg" alt="Image">
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com")
        
        assert result.metrics is not None
        assert result.metrics.elements_extracted > 0


class TestGlobalParserService:
    """Test global parser service instance."""
    
    def test_global_parser_service_exists(self):
        """Test that global parser service exists."""
        from backend.parser.parser_service import parser_service
        
        assert parser_service is not None
        assert isinstance(parser_service, ParserService)
    
    def test_get_parser_service_function(self):
        """Test get_parser_service function."""
        import asyncio
        
        async def test():
            service = await get_parser_service()
            assert isinstance(service, ParserService)
        
        asyncio.run(test())


class TestParserServiceErrorHandling:
    """Test error handling in ParserService."""
    
    @pytest.mark.asyncio
    async def test_parse_exception_handling(self):
        """Test that exceptions are caught and returned as failed result."""
        service = ParserService()
        html = "Not actually HTML"
        
        # Even invalid HTML should be parsed (BeautifulSoup is forgiving)
        result = await service.parse(html, "https://example.com")
        
        # If parsing fails, it should return a failed result
        if not result.success:
            assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_parse_invalid_parser_type(self):
        """Test parsing with invalid parser type."""
        service = ParserService()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        
        # Should fall back to default parser
        result = await service.parse(html, "https://example.com", "invalid")
        
        assert result.success is True
        assert result.url == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])