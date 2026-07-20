"""
Unit tests for parser domain models.
"""

import pytest
from datetime import datetime

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


class TestMetaData:
    """Test cases for MetaData domain model."""
    
    def test_metadata_creation_empty(self):
        """Test creating empty MetaData."""
        metadata = MetaData()
        
        assert metadata.title is None
        assert metadata.description is None
        assert metadata.keywords is None
        assert metadata.canonical_url is None
        assert metadata.language is None
        assert metadata.charset is None
        assert metadata.viewport is None
        assert metadata.robots is None
        assert metadata.author is None
        assert metadata.og_title is None
        assert metadata.og_description is None
        assert metadata.og_image is None
        assert metadata.twitter_card is None
        assert metadata.custom == {}
    
    def test_metadata_creation_full(self):
        """Test creating MetaData with all fields."""
        metadata = MetaData(
            title="Test Title",
            description="Test Description",
            keywords="test,keywords",
            canonical_url="https://example.com",
            language="en",
            charset="utf-8",
            viewport="width=device-width",
            robots="index,follow",
            author="Test Author",
            og_title="OG Title",
            og_description="OG Description",
            og_image="https://example.com/image.jpg",
            twitter_card="summary",
            custom={"custom-tag": "value"}
        )
        
        assert metadata.title == "Test Title"
        assert metadata.description == "Test Description"
        assert metadata.keywords == "test,keywords"
        assert metadata.canonical_url == "https://example.com"
        assert metadata.language == "en"
        assert metadata.charset == "utf-8"
        assert metadata.viewport == "width=device-width"
        assert metadata.robots == "index,follow"
        assert metadata.author == "Test Author"
        assert metadata.og_title == "OG Title"
        assert metadata.og_description == "OG Description"
        assert metadata.og_image == "https://example.com/image.jpg"
        assert metadata.twitter_card == "summary"
        assert metadata.custom == {"custom-tag": "value"}


class TestHeading:
    """Test cases for Heading domain model."""
    
    def test_heading_creation(self):
        """Test creating Heading."""
        heading = Heading(
            level=1,
            text="Main Heading",
            html_content="<h1>Main Heading</h1>",
            attributes={"class": "main-heading"}
        )
        
        assert heading.level == 1
        assert heading.text == "Main Heading"
        assert heading.html_content == "<h1>Main Heading</h1>"
        assert heading.attributes == {"class": "main-heading"}
    
    def test_heading_minimal(self):
        """Test creating minimal Heading."""
        heading = Heading(level=2, text="Subheading")
        
        assert heading.level == 2
        assert heading.text == "Subheading"
        assert heading.html_content is None
        assert heading.attributes == {}


class TestLink:
    """Test cases for Link domain model."""
    
    def test_link_creation_internal(self):
        """Test creating internal link."""
        link = Link(
            url="https://example.com/page",
            text="Page Link",
            title="Link Title",
            rel="nofollow",
            is_internal=True,
            is_nofollow=True
        )
        
        assert link.url == "https://example.com/page"
        assert link.text == "Page Link"
        assert link.title == "Link Title"
        assert link.rel == "nofollow"
        assert link.is_internal is True
        assert link.is_nofollow is True
    
    def test_link_creation_external(self):
        """Test creating external link."""
        link = Link(
            url="https://external.com",
            is_internal=False,
            is_nofollow=False
        )
        
        assert link.url == "https://external.com"
        assert link.is_internal is False
        assert link.is_nofollow is False


class TestImage:
    """Test cases for Image domain model."""
    
    def test_image_creation_full(self):
        """Test creating Image with all fields."""
        image = Image(
            src="https://example.com/image.jpg",
            alt="Image Description",
            title="Image Title",
            width=800,
            height=600,
            is_internal=True
        )
        
        assert image.src == "https://example.com/image.jpg"
        assert image.alt == "Image Description"
        assert image.title == "Image Title"
        assert image.width == 800
        assert image.height == 600
        assert image.is_internal is True
    
    def test_image_creation_minimal(self):
        """Test creating minimal Image."""
        image = Image(src="https://example.com/image.jpg")
        
        assert image.src == "https://example.com/image.jpg"
        assert image.alt is None
        assert image.title is None
        assert image.width is None
        assert image.height is None
        assert image.is_internal is False


class TestScript:
    """Test cases for Script domain model."""
    
    def test_script_with_src(self):
        """Test creating Script with external source."""
        script = Script(
            src="https://cdn.example.com/script.js",
            type="text/javascript",
            async_flag=True,
            defer=False
        )
        
        assert script.src == "https://cdn.example.com/script.js"
        assert script.content is None
        assert script.type == "text/javascript"
        assert script.async_flag is True
        assert script.defer is False
    
    def test_script_inline(self):
        """Test creating inline Script."""
        script = Script(
            content="console.log('Hello World');",
            type="text/javascript"
        )
        
        assert script.src is None
        assert script.content == "console.log('Hello World');"
        assert script.async_flag is False
        assert script.defer is False


class TestStylesheet:
    """Test cases for Stylesheet domain model."""
    
    def test_stylesheet_external(self):
        """Test creating external Stylesheet."""
        stylesheet = Stylesheet(
            href="https://example.com/style.css",
            media="screen",
            is_internal=False
        )
        
        assert stylesheet.href == "https://example.com/style.css"
        assert stylesheet.content is None
        assert stylesheet.media == "screen"
        assert stylesheet.is_internal is False
    
    def test_stylesheet_internal(self):
        """Test creating internal Stylesheet."""
        stylesheet = Stylesheet(
            content="body { color: black; }",
            is_internal=True
        )
        
        assert stylesheet.href is None
        assert stylesheet.content == "body { color: black; }"
        assert stylesheet.is_internal is True


class TestParsingMetrics:
    """Test cases for ParsingMetrics domain model."""
    
    def test_metrics_creation(self):
        """Test creating ParsingMetrics."""
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
    
    def test_metrics_minimal(self):
        """Test creating minimal ParsingMetrics."""
        metrics = ParsingMetrics(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:00:01",
            duration_ms=1000
        )
        
        assert metrics.start_time == "2024-01-01T00:00:00"
        assert metrics.end_time == "2024-01-01T00:00:01"
        assert metrics.duration_ms == 1000
        assert metrics.bytes_processed == 0
        assert metrics.elements_extracted == 0
        assert metrics.parser_type == "unknown"


class TestParserResult:
    """Test cases for ParserResult domain model."""
    
    def test_result_creation_minimal(self):
        """Test creating minimal ParserResult."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>"
        )
        
        assert result.url == "https://example.com"
        assert result.html_content == "<html></html>"
        assert result.title is None
        assert result.text_content is None
        assert result.language is None
        assert result.success is True
        assert result.error is None
    
    def test_result_creation_full(self):
        """Test creating ParserResult with all fields."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            title="Example Page",
            text_content="Page content",
            language="en",
            metadata=MetaData(title="Example Page"),
            success=True
        )
        
        assert result.url == "https://example.com"
        assert result.title == "Example Page"
        assert result.text_content == "Page content"
        assert result.language == "en"
        assert result.success is True
    
    def test_result_with_error(self):
        """Test creating ParserResult with error."""
        result = ParserResult(
            url="https://example.com",
            html_content="",
            success=False,
            error="Empty content"
        )
        
        assert result.success is False
        assert result.error == "Empty content"
    
    def test_post_init_title_sync(self):
        """Test that title is synced from metadata in __post_init__."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html><title>Test</title></html>",
            metadata=MetaData(title="Test from Metadata")
        )
        
        assert result.title == "Test from Metadata"
    
    def test_post_init_error_sets_failure(self):
        """Test that error sets success to False."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            error="Test Error"
        )
        
        assert result.success is False
    
    def test_get_internal_links(self):
        """Test filtering internal links."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            links=[
                Link(url="https://example.com/page", is_internal=True),
                Link(url="https://external.com", is_internal=False),
            ]
        )
        
        internal = result.get_internal_links()
        assert len(internal) == 1
        assert internal[0].url == "https://example.com/page"
    
    def test_get_external_links(self):
        """Test filtering external links."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            links=[
                Link(url="https://example.com/page", is_internal=True),
                Link(url="https://external.com", is_internal=False),
            ]
        )
        
        external = result.get_external_links()
        assert len(external) == 1
        assert external[0].url == "https://external.com"
    
    def test_get_nofollow_links(self):
        """Test filtering nofollow links."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            links=[
                Link(url="https://example.com/page", is_nofollow=True),
                Link(url="https://example.com/other", is_nofollow=False),
            ]
        )
        
        nofollow = result.get_nofollow_links()
        assert len(nofollow) == 1
        assert nofollow[0].url == "https://example.com/page"
    
    def test_get_headings_by_level(self):
        """Test filtering headings by level."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            headings=[
                Heading(level=1, text="H1"),
                Heading(level=2, text="H2a"),
                Heading(level=2, text="H2b"),
                Heading(level=3, text="H3"),
            ]
        )
        
        h2_headings = result.get_headings_by_level(2)
        assert len(h2_headings) == 2
        assert all(h.level == 2 for h in h2_headings)
    
    def test_get_main_heading(self):
        """Test getting main H1 heading."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            headings=[
                Heading(level=2, text="H2"),
                Heading(level=1, text="Main"),
                Heading(level=1, text="Another H1"),
            ]
        )
        
        main_heading = result.get_main_heading()
        assert main_heading is not None
        assert main_heading.level == 1
        assert main_heading.text == "Main"
    
    def test_get_main_heading_none(self):
        """Test getting main heading when none exists."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            headings=[
                Heading(level=2, text="H2"),
                Heading(level=3, text="H3"),
            ]
        )
        
        main_heading = result.get_main_heading()
        assert main_heading is None
    
    def test_has_canonical_url(self):
        """Test checking for canonical URL."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            metadata=MetaData(canonical_url="https://example.com/canonical")
        )
        
        assert result.has_canonical_url() is True
    
    def test_has_no_canonical_url(self):
        """Test when canonical URL is missing."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            metadata=MetaData()
        )
        
        assert result.has_canonical_url() is False
    
    def test_get_structured_content(self):
        """Test getting structured content summary."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            title="Test Page",
            description="Test Description",
            language="en",
            headings=[Heading(level=1, text="Main")],
            links=[Link(url="https://example.com/page", is_internal=True)],
        )
        
        structured = result.get_structured_content()
        
        assert structured["url"] == "https://example.com"
        assert structured["title"] == "Test Page"
        assert structured["description"] == "Test Description"
        assert structured["language"] == "en"
        assert structured["headings_count"] == 1
        assert structured["links_count"] == 1
        assert structured["internal_links_count"] == 1
        assert structured["external_links_count"] == 0
    
    def test_get_text_summary_short(self):
        """Test getting text summary when content is short."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            text_content="Short text content"
        )
        
        summary = result.get_text_summary(100)
        assert summary == "Short text content"
    
    def test_get_text_summary_long(self):
        """Test getting text summary when content is long."""
        long_text = "A" * 600
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            text_content=long_text
        )
        
        summary = result.get_text_summary(500)
        assert len(summary) == 503  # 500 chars + "..."
        assert summary.endswith("...")
    
    def test_get_text_summary_empty(self):
        """Test getting text summary when content is empty."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            text_content=None
        )
        
        summary = result.get_text_summary(100)
        assert summary == ""
    
    def test_validate_no_warnings(self):
        """Test validation with no warnings."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html><head><title>Test</title></head><body>Content</body></html>",
            title="Test",
            metadata=MetaData(description="Test description"),
            language="en"
        )
        
        warnings = result.validate()
        assert len(warnings) == 0
    
    def test_validate_with_warnings(self):
        """Test validation with warnings."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            title=None,
            metadata=MetaData()
        )
        
        warnings = result.validate()
        assert len(warnings) > 0
        assert any("title" in w.lower() for w in warnings)
    
    def test_to_dict_basic(self):
        """Test converting result to dictionary."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            title="Test Page",
            success=True
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["url"] == "https://example.com"
        assert result_dict["title"] == "Test Page"
        assert result_dict["success"] is True
        assert "metadata" in result_dict
        assert "links" in result_dict
        assert "images" in result_dict
        assert "scripts" in result_dict
        assert "stylesheets" in result_dict
    
    def test_to_dict_with_all_fields(self):
        """Test converting result with all fields to dictionary."""
        result = ParserResult(
            url="https://example.com",
            html_content="<html></html>",
            title="Test",
            text_content="Content",
            language="en",
            metadata=MetaData(title="Test"),
            headings=[Heading(level=1, text="Main")],
            links=[Link(url="https://example.com/page", is_internal=True)],
            images=[Image(src="https://example.com/image.jpg", is_internal=True)],
            scripts=[Script(src="https://example.com/script.js")],
            stylesheets=[Stylesheet(href="https://example.com/style.css")],
            success=True,
            metrics=ParsingMetrics(
                start_time="2024-01-01T00:00:00",
                end_time="2024-01-01T00:00:01",
                duration_ms=1000,
                elements_extracted=4,
                parser_type="beautifulsoup"
            )
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["url"] == "https://example.com"
        assert result_dict["title"] == "Test"
        assert result_dict["text_content"] == "Content"
        assert result_dict["language"] == "en"
        assert len(result_dict["headings"]) == 1
        assert len(result_dict["links"]) == 1
        assert len(result_dict["images"]) == 1
        assert len(result_dict["scripts"]) == 1
        assert len(result_dict["stylesheets"]) == 1
        assert result_dict["metrics"]["duration_ms"] == 1000
        assert result_dict["metrics"]["elements_extracted"] == 4
        assert result_dict["structured_content"]["headings_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])