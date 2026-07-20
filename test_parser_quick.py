"""
Quick parser test to verify functionality.
"""

import pytest
import asyncio


def test_parser_domain_models():
    """Test parser domain models."""
    from backend.core.domain.parser import (
        ContentType,
        MetaData,
        Heading,
        Link,
        Image,
        Script,
        Stylesheet,
        ParsingMetrics,
        ParserResult,
    )
    
    def test_metadata_creation():
        """Test creating empty MetaData."""
        metadata = MetaData()
        assert metadata.title is None
        assert metadata.description is None
        assert metadata.keywords is None
        assert metadata.canonical_url is None
        assert metadata.language is None
        assert metadata.charset is None
        assert metadata.og_title is None
        assert metadata.og_description is None
        assert metadata.og_image is None
        assert metadata.twitter_card is None
        assert metadata.custom == {}
    
    def test_heading_creation():
        """Test creating Heading."""
        heading = Heading(level=2, text="Test Heading")
        assert heading.level == 2
        assert heading.text == "Test Heading"
        assert heading.html_content is None
        assert heading.attributes == {}
    
    def test_link_creation_internal():
        """Test creating internal Link."""
        link = Link(url="https://example.com/page", is_internal=True, is_nofollow=False)
        assert link.url == "https://example.com/page"
        assert link.is_internal is True
        assert link.is_nofollow is False
    
    def test_image_creation():
        """Test creating Image."""
        image = Image(src="https://example.com/image.jpg", alt="Test Image")
        assert image.src == "https://example.com/image.jpg"
        assert image.alt == "Test Image"
        assert image.width is None
        assert image.height is None
    
    def test_script_creation_with_src(self):
        """Test creating Script with external source."""
        script = Script(
            src="https://cdn.example.com/script.js",
            type="text/javascript",
            async_flag=True
        )
        assert script.src == "https://cdn.example.com/script.js"
        assert script.type == "text/javascript"
        assert script.async_flag is True
    
    def test_parsing_metrics():
        """Test ParsingMetrics creation."""
        metrics = ParsingMetrics(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:00:01",
            duration_ms=1000,
            bytes_processed=50000,
            elements_extracted=25,
            parser_type="beautifulsoup"
        )
        assert metrics.start_time == "2024-01-01T00:00:00"
        assert metrics.end_time == "2024-01-01T00:00:01"
        assert metrics.duration_ms == 1000
        assert metrics.bytes_processed == 50000
        assert metrics.elements_extracted == 25
        assert metrics.parser_type == "beautifulsoup"
    
    def test_parser_result_creation():
        """Test creating ParserResult."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html><body>Content</body></html>",
            title="Test Page"
        )
        
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.success is True
        assert result.error is None
    
    def test_parser_result_with_error():
        """Test creating ParserResult with error."""
        result = ParserResult(
            url="https://example.com",
            html_content="",
            success=False,
            error="Empty content"
        )
        
        assert result.success is False
        assert result.error == "Empty content"
    
    def test_parser_result_validation_empty():
        """Test validation of empty ParserResult."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>"
        )
        
        warnings = result.validate()
        
        # Empty page should generate warnings
        assert len(warnings) > 0
        assert any("title" in w.lower() for w in warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])