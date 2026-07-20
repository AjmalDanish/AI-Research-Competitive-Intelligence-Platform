"""
Unit tests for IParser interface implementations.
"""

import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from backend.core.interfaces.parser import IParser
from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupParser
from backend.parser.implementations.trafilatura_parser import TrafilaturaParser
from backend.core.domain.parser import (
    ParserResult,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
)


class TestIParserInterface:
    """Test IParser interface compliance."""
    
    def test_beautifulsoup_parser_implements_interface(self):
        """Test that BeautifulSoupParser implements IParser."""
        parser = BeautifulSoupParser()
        assert isinstance(parser, IParser)
    
    def test_trafilatura_parser_implements_interface(self):
        """Test that TrafilaturaParser implements IParser."""
        parser = TrafilaturaParser()
        assert isinstance(parser, IParser)
    
    def test_parser_name_property(self):
        """Test parser_name property is implemented."""
        bs_parser = BeautifulSoupParser()
        tf_parser = TrafilaturaParser()
        
        assert bs_parser.parser_name == "beautifulsoup"
        assert tf_parser.parser_name == "trafilatura"
    
    def test_parse_method_signature(self):
        """Test parse method has correct signature."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'parse')
        assert callable(parser.parse)
    
    def test_can_parse_method_exists(self):
        """Test can_parse method exists."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'can_parse')
        assert callable(parser.can_parse)
    
    def test_extract_title_method_exists(self):
        """Test extract_title method exists."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'extract_title')
        assert callable(parser.extract_title)
    
    def test_extract_text_content_method_exists(self):
        """Test extract_text_content method exists."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'extract_text_content')
        assert callable(parser.extract_text_content)
    
    def test_detect_language_method_exists(self):
        """Test detect_language method exists."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'detect_language')
        assert callable(parser.detect_language)
    
    def test_extract_metadata_method_exists(self):
        """Test extract_metadata method exists."""
        parser = BeautifulSoupParser()
        
        # Check method exists
        assert hasattr(parser, 'extract_metadata')
        assert callable(parser.extract_metadata)


class TestURLHelpers:
    """Test URL helper methods from IParser interface."""
    
    def test_normalize_url_absolute(self):
        """Test normalizing absolute URL."""
        parser = BeautifulSoupParser()
        url = parser.normalize_url("https://example.com/page", "https://example.com")
        
        assert url == "https://example.com/page"
    
    def test_normalize_url_relative(self):
        """Test normalizing relative URL."""
        parser = BeautifulSoupParser()
        url = parser.normalize_url("/page", "https://example.com")
        
        assert url == "https://example.com/page"
    
    def test_normalize_url_protocol_relative(self):
        """Test normalizing protocol-relative URL."""
        parser = BeautifulSoupParser()
        url = parser.normalize_url("//cdn.example.com/script.js", "https://example.com")
        
        assert url == "https://cdn.example.com/script.js"
    
    def test_normalize_url_nested_relative(self):
        """Test normalizing nested relative URL."""
        parser = BeautifulSoupParser()
        url = parser.normalize_url("other/page", "https://example.com/some/path")
        
        assert url == "https://example.com/some/path/other/page"
    
    def test_is_internal_url_true(self):
        """Test identifying internal URL."""
        parser = BeautifulSoupParser()
        is_internal = parser.is_internal_url("https://example.com/page", "https://example.com")
        
        assert is_internal is True
    
    def test_is_internal_url_false(self):
        """Test identifying external URL."""
        parser = BeautifulSoupParser()
        is_internal = parser.is_internal_url("https://external.com/page", "https://example.com")
        
        assert is_internal is False
    
    def test_is_internal_url_subdomain(self):
        """Test identifying subdomain as internal."""
        parser = BeautifulSoupParser()
        is_internal = parser.is_internal_url("https://blog.example.com/page", "https://example.com")
        
        assert is_internal is False
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        parser = BeautifulSoupParser()
        text = parser.clean_text("  hello   world  ")
        
        assert text == "hello world"
    
    def test_clean_text_with_newlines(self):
        """Test cleaning text with newlines."""
        parser = BeautifulSoupParser()
        text = parser.clean_text("line1\\n\\nline2\\r\\rline3")
        
        assert text == "line1 line2 line3"
    
    def test_clean_text_with_tabs(self):
        """Test cleaning text with tabs."""
        parser = BeautifulSoupParser()
        text = parser.clean_text("hello\\tworld")
        
        assert text == "hello world"
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        parser = BeautifulSoupParser()
        text = parser.clean_text("")
        
        assert text == ""
    
    def test_clean_text_none(self):
        """Test cleaning None text."""
        parser = BeautifulSoupParser()
        text = parser.clean_text(None)
        
        assert text == ""


class TestBeautifulSoupParserBasic:
    """Basic tests for BeautifulSoupParser."""
    
    def test_parser_initialization(self):
        """Test BeautifulSoupParser initialization."""
        parser = BeautifulSoupParser(encoding="utf-8")
        
        assert parser.parser_name == "beautifulsoup"
        assert parser.encoding == "utf-8"
    
    def test_can_parse_empty_content(self):
        """Test can_parse with empty content."""
        parser = BeautifulSoupParser()
        
        assert parser.can_parse("") is False
    
    def test_can_parse_valid_html(self):
        """Test can_parse with valid HTML."""
        parser = BeautifulSoupParser()
        
        assert parser.can_parse("<html><body>Content</body></html>") is True
    
    def test_can_parse_with_html_indicators(self):
        """Test can_parse detects HTML indicators."""
        parser = BeautifulSoupParser()
        
        # Various HTML indicators
        html_samples = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<body>",
            "<div>",
            "<p>",
        ]
        
        for sample in html_samples:
            assert parser.can_parse(sample) is True
    
    def test_extract_title_no_html(self):
        """Test extract_title with no HTML."""
        parser = BeautifulSoupParser()
        title = parser.extract_title("plain text")
        
        assert title is None
    
    def test_extract_title_with_title(self):
        """Test extract_title with title tag."""
        parser = BeautifulSoupParser()
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        title = parser.extract_title(html)
        
        assert title == "Test Page"
    
    def test_extract_title_with_whitespace(self):
        """Test extract_title with whitespace."""
        parser = BeautifulSoupParser()
        html = "<html><head><title>  Test Page  </title></head><body></body></html>"
        title = parser.extract_title(html)
        
        assert title == "Test Page"
    
    def test_extract_text_content_basic(self):
        """Test extract_text_content with basic HTML."""
        parser = BeautifulSoupParser()
        html = "<html><body><p>Test paragraph</p></body></html>"
        text = parser.extract_text_content(html)
        
        assert "Test paragraph" in text
    
    def test_extract_text_content_removes_scripts(self):
        """Test extract_text_content removes script content."""
        parser = BeautifulSoupParser()
        html = "<html><body><p>Content</p><script>var x = 1;</script></body></html>"
        text = parser.extract_text_content(html)
        
        assert "Content" in text
        assert "var x = 1" not in text
    
    def test_extract_text_content_removes_styles(self):
        """Test extract_text_content removes style content."""
        parser = BeautifulSoupParser()
        html = "<html><body><p>Content</p><style>body { color: red; }</style></body></html>"
        text = parser.extract_text_content(html)
        
        assert "Content" in text
        assert "color: red" not in text
    
    def test_detect_language_from_html_tag(self):
        """Test language detection from html tag."""
        parser = BeautifulSoupParser()
        html = '<html lang="en"><body>Content</body></html>'
        language = parser.detect_language(html)
        
        assert language == "en"
    
    def test_detect_language_from_body_tag(self):
        """Test language detection from body tag."""
        parser = BeautifulSoupParser()
        html = '<html><body lang="es">Content</body></html>'
        language = parser.detect_language(html)
        
        assert language == "es"
    
    def test_detect_language_no_language(self):
        """Test language detection when no language specified."""
        parser = BeautifulSoupParser()
        html = '<html><body>Content</body></html>'
        language = parser.detect_language(html)
        
        assert language is None
    
    def test_extract_metadata_empty_html(self):
        """Test extract_metadata with empty HTML."""
        parser = BeautifulSoupParser()
        html = "<html></html>"
        
        # Import BeautifulSoup for creating soup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        metadata_dict = parser.extract_metadata(soup, html)
        
        assert isinstance(metadata_dict, MetaData)
        assert metadata_dict.title is None
        assert metadata_dict.description is None


class TestTrafilaturaParserBasic:
    """Basic tests for TrafilaturaParser."""
    
    def test_parser_initialization(self):
        """Test TrafilaturaParser initialization."""
        parser = TrafilaturaParser()
        
        assert parser.parser_name == "trafilatura"
        assert parser.config is not None
    
    def test_can_parse_empty_content(self):
        """Test can_parse with empty content."""
        parser = TrafilaturaParser()
        
        assert parser.can_parse("") is False
    
    def test_can_parse_valid_html(self):
        """Test can_parse with valid HTML."""
        parser = TrafilaturaParser()
        
        assert parser.can_parse("<html><body>Content</body></html>") is True


class TestBeautifulSoupParserAsync:
    """Async tests for BeautifulSoupParser."""
    
    @pytest.mark.asyncio
    async def test_parse_success(self):
        """Test successful parsing."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test Description">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>Test paragraph</p>
        </body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = BeautifulSoupParser()
        
        result = await parser.parse("", "https://example.com")
        
        assert result.success is False
        assert result.error == "Empty HTML content provided"
    
    @pytest.mark.asyncio
    async def test_parse_with_options(self):
        """Test parsing with options."""
        parser = BeautifulSoupParser()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        options = {
            "start_time": "2024-01-01T00:00:00",
            "duration_ms": 500,
        }
        
        result = await parser.parse(html, "https://example.com", options)
        
        assert result.success is True
        assert result.metrics is not None
        assert result.metrics.start_time == "2024-01-01T00:00:00"
    
    @pytest.mark.asyncio
    async def test_parse_complex_html(self):
        """Test parsing complex HTML with multiple elements."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <head>
            <title>Complex Page</title>
            <meta name="description" content="A complex test page">
            <link rel="canonical" href="https://example.com/complex">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading 1</h2>
            <h2>Subheading 2</h2>
            <h3>Detail heading</h3>
            <p>Test paragraph with <a href="https://example.com/link">link</a></p>
            <img src="/image.jpg" alt="Test Image">
            <script src="/script.js"></script>
            <link rel="stylesheet" href="/style.css">
        </body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert result.title == "Complex Page"
        assert result.metadata.description == "A complex test page"
        assert result.metadata.canonical_url == "https://example.com/complex"
        assert len(result.headings) == 4  # 1x h1, 2x h2, 1x h3
        assert len(result.links) == 1
        assert len(result.images) == 1
        assert len(result.scripts) == 1
        assert len(result.stylesheets) == 1
    
    @pytest.mark.asyncio
    async def test_parse_with_links(self):
        """Test parsing HTML with various link types."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <body>
            <a href="https://example.com/internal">Internal Link</a>
            <a href="https://external.com">External Link</a>
            <a href="https://example.com/no" rel="nofollow">Nofollow Link</a>
            <a href="/relative">Relative Link</a>
        </body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert len(result.links) == 4
        
        # Check internal/external classification
        internal_links = result.get_internal_links()
        external_links = result.get_external_links()
        nofollow_links = result.get_nofollow_links()
        
        assert len(internal_links) == 2  # Internal and relative
        assert len(external_links) == 1  # Only external
        assert len(nofollow_links) == 1  # Only the nofollow one
    
    @pytest.mark.asyncio
    async def test_parse_with_images(self):
        """Test parsing HTML with images."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <body>
            <img src="https://example.com/image1.jpg" alt="Image 1" width="800" height="600">
            <img src="/image2.jpg" alt="Image 2">
            <img src="https://cdn.com/image3.jpg" alt="Image 3" width="1024">
        </body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert len(result.images) == 3
        
        # Check image properties
        first_image = result.images[0]
        assert first_image.src == "https://example.com/image1.jpg"
        assert first_image.alt == "Image 1"
        assert first_image.width == 800
        assert first_image.height == 600
        assert first_image.is_internal is True
    
    @pytest.mark.asyncio
    async def test_parse_with_scripts(self):
        """Test parsing HTML with scripts."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <head>
            <script src="/script.js"></script>
            <script type="text/javascript">console.log('inline script');</script>
            <script src="/async.js" async></script>
            <script src="/defer.js" defer></script>
        </head>
        <body>Content</body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert len(result.scripts) == 4
        
        # Check script properties
        async_script = next((s for s in result.scripts if s.async_flag), None)
        defer_script = next((s for s in result.scripts if s.defer), None)
        
        assert async_script is not None
        assert defer_script is not None
    
    @pytest.mark.asyncio
    async def test_parse_with_stylesheets(self):
        """Test parsing HTML with stylesheets."""
        parser = BeautifulSoupParser()
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="/style.css">
            <link rel="stylesheet" href="https://cdn.com/external.css" media="screen">
            <style>body { color: black; }</style>
        </head>
        <body>Content</body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert len(result.stylesheets) == 3
        
        # Check stylesheet properties
        external_ss = next((s for s in result.stylesheets if not s.is_internal), None)
        internal_ss = next((s for s in result.stylesheets if s.is_internal), None)
        inline_ss = next((s for s in result.stylesheets if s.content is not None), None)
        
        assert external_ss is not None
        assert internal_ss is not None
        assert inline_ss is not None
    
    @pytest.mark.asyncio
    async def test_parse_error_handling(self):
        """Test error handling in parse method."""
        parser = BeautifulSoupParser()
        
        # Create malformed HTML that might cause issues
        malformed_html = """
        <html>
        <head>
            <title>Malformed</title>
        </head>
        <body>
            <p>Test
        </body>
        """
        
        result = await parser.parse(malformed_html, "https://example.com")
        
        # BeautifulSoup is quite forgiving, so it might succeed
        # If it fails, it should have an error
        if not result.success:
            assert result.error is not None


class TestTrafilaturaParserAsync:
    """Async tests for TrafilaturaParser."""
    
    @pytest.mark.asyncio
    async def test_parse_success(self):
        """Test successful parsing."""
        parser = TrafilaturaParser()
        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test Description">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>Test paragraph</p>
        </body>
        </html>
        """
        
        result = await parser.parse(html, "https://example.com")
        
        assert result.success is True
        assert result.url == "https://example.com"
        # Trafilatura might extract text content and title
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = TrafilaturaParser()
        
        result = await parser.parse("", "https://example.com")
        
        assert result.success is False
        assert result.error == "Empty HTML content provided"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])