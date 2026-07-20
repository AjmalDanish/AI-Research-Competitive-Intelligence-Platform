# Parser Extension Guide

## Overview

This guide explains how to add new parser implementations to the AI Website Intelligence Platform without modifying existing code, following the **Open/Closed Principle** from SOLID design principles.

## Open/Closed Principle

**"Software entities should be open for extension, but closed for modification."**

In the context of the Parser Foundation:
- ✅ **Open for extension**: New parsers can be added by implementing the `IParser` interface
- ❌ **Closed for modification**: Existing parsers (`BeautifulSoupParser`, `TrafilaturaParser`) are never modified

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     IParser Interface                             │
│                 (Abstract Base Class)                             │
│                                                                   │
│  + parse(html: str, url: Optional[str]) -> ParserResult         │
│  + extract_title(html: str) -> Optional[str]                     │
│  + extract_text_content(html: str) -> str                        │
│  + detect_language(html: str) -> Optional[str]                   │
│  + extract_metadata(html: str) -> MetaData                       │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │ implements
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        │                 │                 │
┌───────┴──────┐  ┌──────┴───────┐  ┌──────┴────────┐
│BeautifulSoup │  │ Trafilatura  │  │   Custom     │
│   Parser     │  │   Parser     │  │   Parser     │
└──────────────┘  └──────────────┘  └───────────────┘

No existing code needs modification when adding CustomParser!
```

## Step-by-Step Guide

### Step 1: Create Parser Implementation File

**Location**: `backend/parser/implementations/your_parser.py`

**Template**:
```python
"""
Custom Parser Implementation

This parser demonstrates how to create a new parser implementation
following the IParser interface without modifying existing code.
"""

from typing import Optional
from backend.core.interfaces.parser import IParser
from backend.core.domain.parser import (
    ParserResult,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
    ParsingMetrics,
)
from backend.parser.exceptions import ParserError


class CustomParser(IParser):
    """
    Custom parser implementation for specific use cases.

    This class demonstrates the Open/Closed Principle:
    - Implements IParser interface
    - No modification to existing parsers needed
    - Can be used immediately with ParserService
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the custom parser.

        Args:
            config: Optional configuration dictionary for parser behavior
        """
        self.config = config or {}
        # Initialize your parser-specific resources here
        self.user_agent = self.config.get("user_agent", "CustomParser/1.0")

    def parse(
        self,
        html: str,
        url: Optional[str] = None
    ) -> ParserResult:
        """
        Parse HTML content and return structured result.

        Args:
            html: HTML content to parse
            url: Optional URL for link classification

        Returns:
            ParserResult with extracted content

        Raises:
            ParserError: If parsing fails
        """
        try:
            import time  # For metrics tracking
            start_time = time.time()

            # Extract all content components
            title = self.extract_title(html) or "Untitled"
            text_content = self.extract_text_content(html)
            metadata = self.extract_metadata(html)

            # Extract structured content
            headings = self._extract_headings(html)
            links = self._extract_links(html, url)
            images = self._extract_images(html)
            scripts = self._extract_scripts(html)
            stylesheets = self._extract_stylesheets(html)

            # Calculate metrics
            end_time = time.time()
            metrics = self._create_metrics(
                html, text_content, headings, links, images,
                scripts, stylesheets, end_time - start_time
            )

            return ParserResult(
                url=url or "",
                title=title,
                content=html,
                text_content=text_content,
                metadata=metadata,
                headings=headings,
                links=links,
                images=images,
                scripts=scripts,
                stylesheets=stylesheets,
                metrics=metrics
            )

        except Exception as e:
            raise ParserError(f"Custom parsing failed: {str(e)}") from e

    def extract_title(self, html: str) -> Optional[str]:
        """
        Extract title from HTML.

        Args:
            html: HTML content

        Returns:
            Extracted title or None
        """
        # Implement your title extraction logic here
        # Example using regex or your preferred method
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return title_match.group(1).strip() if title_match else None

    def extract_text_content(self, html: str) -> str:
        """
        Extract main text content from HTML.

        Args:
            html: HTML content

        Returns:
            Cleaned text content
        """
        # Implement your text extraction logic here
        # Example: basic tag removal
        import re
        # Remove script and style tags
        clean_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.IGNORECASE | re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', clean_html)
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def detect_language(self, html: str) -> Optional[str]:
        """
        Detect content language.

        Args:
            html: HTML content

        Returns:
            Detected language code or None
        """
        # Implement your language detection logic here
        # Example: check HTML lang attribute
        import re
        lang_match = re.search(r'<html[^>]*lang=["\']([^"\']+)["\']', html, re.IGNORECASE)
        return lang_match.group(1) if lang_match else None

    def extract_metadata(self, html: str) -> MetaData:
        """
        Extract metadata from HTML.

        Args:
            html: HTML content

        Returns:
            MetaData object with extracted metadata
        """
        # Extract basic metadata
        title = self.extract_title(html) or ""

        # Extract description
        import re
        description = None
        desc_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        if desc_match:
            description = desc_match.group(1)

        # Extract keywords
        keywords = []
        keywords_match = re.search(
            r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        if keywords_match:
            keywords = [k.strip() for k in keywords_match.group(1).split(',')]

        # Extract Open Graph data
        og_data = {}
        og_matches = re.findall(
            r'<meta[^>]*property=["\']og:([^"\']+)["\'][^>]*content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        for prop, content in og_matches:
            og_data[prop] = content

        # Extract Twitter card data
        twitter_data = {}
        twitter_matches = re.findall(
            r'<meta[^>]*name=["\']twitter:([^"\']+)["\'][^>]*content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        for prop, content in twitter_matches:
            twitter_data[prop] = content

        return MetaData(
            title=title,
            description=description,
            keywords=keywords,
            canonical_url=None,
            og_data=og_data,
            twitter_data=twitter_data,
            author=None,
            publish_date=None,
            language=self.detect_language(html),
            content_type=None
        )

    def _extract_headings(self, html: str) -> list[Heading]:
        """Extract headings from HTML."""
        import re
        headings = []
        for level in range(1, 7):
            pattern = rf'<h{level}[^>]*>(.*?)</h{level}>'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for i, match in enumerate(matches):
                clean_text = re.sub(r'<[^>]+>', '', match).strip()
                headings.append(Heading(
                    level=level,
                    text=clean_text,
                    position=len(headings)
                ))
        return headings

    def _extract_links(self, html: str, url: Optional[str] = None) -> list[Link]:
        """Extract links from HTML."""
        import re
        from urllib.parse import urlparse

        links = []
        base_domain = urlparse(url).netloc if url else None

        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)

        for link_url, link_text in matches:
            clean_text = re.sub(r'<[^>]+>', '', link_text).strip()

            # Classify as internal/external
            is_external = False
            if base_domain:
                link_domain = urlparse(link_url).netloc
                is_external = link_domain and link_domain != base_domain

            links.append(Link(
                url=link_url,
                text=clean_text if clean_text else None,
                title=None,
                is_external=is_external,
                is_nofollow=False,
                position=len(links)
            ))

        return links

    def _extract_images(self, html: str) -> list[Image]:
        """Extract images from HTML."""
        import re
        images = []

        image_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*(?:width=["\'](\d+)["\'])?[^>]*(?:height=["\'](\d+)["\'])?'
        matches = re.findall(image_pattern, html, re.IGNORECASE)

        for src, alt, width, height in matches:
            images.append(Image(
                url=src,
                alt_text=alt if alt else None,
                title=None,
                width=int(width) if width else None,
                height=int(height) if height else None,
                position=len(images)
            ))

        return images

    def _extract_scripts(self, html: str) -> list[Script]:
        """Extract scripts from HTML."""
        import re
        scripts = []

        # External scripts
        external_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*(?:type=["\']([^"\']*)["\'])?[^>]*>'
        external_matches = re.findall(external_pattern, html, re.IGNORECASE)

        for src, script_type in external_matches:
            scripts.append(Script(
                url=src,
                content=None,
                type=script_type if script_type else None,
                is_async=False,
                is_defer=False,
                position=len(scripts)
            ))

        # Inline scripts
        inline_pattern = r'<script[^>]*>(.*?)</script>'
        inline_matches = re.findall(inline_pattern, html, re.IGNORECASE | re.DOTALL)

        for content in inline_matches:
            scripts.append(Script(
                url=None,
                content=content.strip() if content.strip() else None,
                type=None,
                is_async=False,
                is_defer=False,
                position=len(scripts)
            ))

        return scripts

    def _extract_stylesheets(self, html: str) -> list[Stylesheet]:
        """Extract stylesheets from HTML."""
        import re
        stylesheets = []

        link_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*(?:media=["\']([^"\']*)["\'])?[^>]*(?:title=["\']([^"\']*)["\'])?'
        matches = re.findall(link_pattern, html, re.IGNORECASE)

        for href, media, title in matches:
            stylesheets.append(Stylesheet(
                url=href,
                media=media if media else None,
                title=title if title else None,
                position=len(stylesheets)
            ))

        return stylesheets

    def _create_metrics(
        self,
        html: str,
        text_content: str,
        headings: list,
        links: list,
        images: list,
        scripts: list,
        stylesheets: list,
        duration: float
    ) -> ParsingMetrics:
        """Create parsing metrics."""
        return ParsingMetrics(
            parse_duration_seconds=duration,
            content_length=len(html),
            text_length=len(text_content),
            heading_count=len(headings),
            link_count=len(links),
            image_count=len(images),
            script_count=len(scripts),
            stylesheet_count=len(stylesheets),
            parser_used=self.__class__.__name__
        )
```

### Step 2: Update Module Exports

**File**: `backend/parser/implementations/__init__.py`

**Add your parser to exports**:
```python
"""
Parser implementations module.

This module exports all available parser implementations.
Following Open/Closed Principle: new parsers can be added
without modifying existing code.
"""

from backend.parser.implementations.beautifulsoup_parser import (
    BeautifulSoupParser,
    BeautifulSoupConfig,
)
from backend.parser.implementations.trafilatura_parser import (
    TrafilaturaParser,
    TrafilaturaConfig,
)
from backend.parser.implementations.your_parser import CustomParser  # Add this line

__all__ = [
    "BeautifulSoupParser",
    "BeautifulSoupConfig",
    "TrafilaturaParser",
    "TrafilaturaConfig",
    "CustomParser",  # Add this line
]
```

### Step 3: Update Main Parser Module Exports

**File**: `backend/parser/__init__.py`

**Add your parser to main exports**:
```python
"""
Parser module - HTML parsing capabilities.

This module provides access to parsing functionality including:
- ParserService for orchestration
- Multiple parser implementations
- Parser-specific exceptions
- Domain models for structured content

Open/Closed Principle: New parsers can be added without modifying existing code.
"""

from backend.parser.parser_service import ParserService
from backend.parser.exceptions import (
    ParserError,
    ParserNotAvailableError,
    ParseTimeoutError,
    InvalidHTMLError,
)

# Import available parser implementations
from backend.parser.implementations.beautifulsoup_parser import (
    BeautifulSoupParser,
    BeautifulSoupConfig,
)
from backend.parser.implementations.trafilatura_parser import (
    TrafilaturaParser,
    TrafilaturaConfig,
)
from backend.parser.implementations.your_parser import CustomParser  # Add this line

# Domain models
from backend.core.domain.parser import (
    ParserResult,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
    ParsingMetrics,
)

__all__ = [
    # Service
    "ParserService",

    # Exceptions
    "ParserError",
    "ParserNotAvailableError",
    "ParseTimeoutError",
    "InvalidHTMLError",

    # Parsers
    "BeautifulSoupParser",
    "BeautifulSoupConfig",
    "TrafilaturaParser",
    "TrafilaturaConfig",
    "CustomParser",  # Add this line

    # Domain models
    "ParserResult",
    "MetaData",
    "Heading",
    "Link",
    "Image",
    "Script",
    "Stylesheet",
    "ParsingMetrics",
]
```

### Step 4: Use Your Custom Parser

**Instantiating the Parser**:
```python
from backend.parser import ParserService, CustomParser

# Create service with your custom parser
service = ParserService(
    primary_parser=CustomParser(),
    enable_fallback=False
)

# Parse content
result = service.parse(html, url="https://example.com")
print(f"Title: {result.title}")
print(f"Content: {result.text_content}")
```

**With Configuration**:
```python
from backend.parser import ParserService, CustomParser

# Configure your parser
config = {
    "user_agent": "MyCustomParser/1.0",
    "custom_setting": "value"
}

service = ParserService(
    primary_parser=CustomParser(config=config),
    enable_fallback=True
)
```

**As Fallback Parser**:
```python
from backend.parser import ParserService, BeautifulSoupParser, CustomParser

service = ParserService(
    primary_parser=BeautifulSoupParser(),
    fallback_parser=CustomParser(),  # Use as fallback
    enable_fallback=True
)
```

### Step 5: Add Tests (Optional but Recommended)

**File**: `backend/tests/unit/parser/test_custom_parser.py`

```python
"""
Unit tests for CustomParser implementation.
"""

import pytest
from backend.parser import CustomParser
from backend.core.domain.parser import ParserResult
from backend.parser.exceptions import ParserError


class TestCustomParser:
    """Test suite for CustomParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return CustomParser()

    @pytest.fixture
    def sample_html(self):
        """Sample HTML for testing."""
        return """
        <html lang="en">
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, parser, html">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>Test content paragraph.</p>
            <a href="https://example.com">External Link</a>
            <img src="image.jpg" alt="Test Image" width="100" height="50">
        </body>
        </html>
        """

    def test_parse_success(self, parser, sample_html):
        """Test successful parsing."""
        result = parser.parse(sample_html, url="https://test.com")

        assert isinstance(result, ParserResult)
        assert result.title == "Test Page"
        assert "Test content paragraph" in result.text_content
        assert result.metadata.description == "Test description"
        assert len(result.headings) > 0
        assert len(result.links) > 0
        assert len(result.images) > 0

    def test_extract_title(self, parser, sample_html):
        """Test title extraction."""
        title = parser.extract_title(sample_html)
        assert title == "Test Page"

    def test_extract_text_content(self, parser, sample_html):
        """Test text content extraction."""
        content = parser.extract_text_content(sample_html)
        assert "Test content paragraph" in content
        assert "<" not in content  # No HTML tags

    def test_detect_language(self, parser, sample_html):
        """Test language detection."""
        language = parser.detect_language(sample_html)
        assert language == "en"

    def test_extract_metadata(self, parser, sample_html):
        """Test metadata extraction."""
        metadata = parser.extract_metadata(sample_html)

        assert metadata.title == "Test Page"
        assert metadata.description == "Test description"
        assert "test" in metadata.keywords
        assert "parser" in metadata.keywords

    def test_parse_empty_html(self, parser):
        """Test parsing empty HTML."""
        with pytest.raises(ParserError):
            parser.parse("", url="https://test.com")

    def test_parse_invalid_html(self, parser):
        """Test parsing invalid HTML."""
        with pytest.raises(ParserError):
            parser.parse("<<invalid>>", url="https://test.com")

    def test_parse_without_url(self, parser, sample_html):
        """Test parsing without URL."""
        result = parser.parse(sample_html)
        assert result.url == ""
        assert result.title == "Test Page"

    def test_metrics_collection(self, parser, sample_html):
        """Test that metrics are collected."""
        result = parser.parse(sample_html, url="https://test.com")

        assert result.metrics.parse_duration_seconds > 0
        assert result.metrics.content_length > 0
        assert result.metrics.text_length > 0
        assert result.metrics.parser_used == "CustomParser"
```

## Advanced: Parser Selection Strategy

To make your parser selectable by `ParserService.recommend_parser()`, extend the recommendation logic:

**File**: `backend/parser/parser_service.py`

**Add recommendation logic for your parser**:
```python
def recommend_parser(
    self,
    url: Optional[str] = None,
    content_type: Optional[str] = None
) -> str:
    """
    Recommend best parser for given content.

    Args:
        url: Optional URL to analyze for parser recommendation
        content_type: Optional content type string (e.g., `"text/html"`, `"article"`)

    Returns:
        Recommended parser type
    """
    # Add your custom parser recommendation logic here
    if url and "special-case.com" in url:
        return "custom"  # Return your parser type

    if content_type and "special" in content_type:
        return "custom"

    # Existing logic for other parsers
    if content_type and "article" in content_type:
        return "trafilatura"

    return "beautifulsoup"
```

## Advanced: Parser Configuration

Create a configuration class for your parser:

**File**: `backend/parser/implementations/your_parser.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomParserConfig:
    """Configuration for CustomParser."""

    user_agent: str = "CustomParser/1.0"
    timeout_seconds: int = 30
    max_content_length: int = 10_000_000
    custom_option: str = "default_value"
    enable_advanced_features: bool = False

    def validate(self) -> None:
        """Validate configuration."""
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_content_length <= 0:
            raise ValueError("max_content_length must be positive")


class CustomParser(IParser):
    """Custom parser with configuration."""

    def __init__(self, config: Optional[CustomParserConfig] = None):
        """
        Initialize parser with configuration.

        Args:
            config: Optional configuration object
        """
        self.config = config or CustomParserConfig()
        self.config.validate()  # Validate configuration
```

**Usage with configuration**:
```python
from backend.parser import CustomParser, CustomParserConfig

# Create custom configuration
config = CustomParserConfig(
    user_agent="MyBot/2.0",
    timeout_seconds=60,
    max_content_length=20_000_000,
    custom_option="special_value",
    enable_advanced_features=True
)

# Create parser with configuration
parser = CustomParser(config=config)

# Use with ParserService
service = ParserService(primary_parser=parser)
```

## Testing Your Implementation

### **Unit Tests**
```bash
# Run unit tests for your parser
python -m pytest backend/tests/unit/parser/test_custom_parser.py -v
```

### **Integration Tests**
```bash
# Run integration tests
python -m pytest backend/tests/integration/test_parser_integration.py -v
```

### **Quality Checks**
```bash
# Format code
python -m black backend/parser/implementations/your_parser.py

# Lint code
python -m ruff check backend/parser/implementations/your_parser.py

# Type check
python -m mypy backend/parser/implementations/your_parser.py
```

## Best Practices

### **1. Error Handling**
```python
def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
    try:
        # Your parsing logic
        pass
    except Exception as e:
        # Always wrap errors in ParserError
        raise ParserError(f"Custom parser failed: {str(e)}") from e
```

### **2. Performance Considerations**
```python
import time

def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
    start_time = time.time()
    try:
        # Your parsing logic
        result = ParserResult(...)
        end_time = time.time()

        # Always include performance metrics
        result.metrics.parse_duration_seconds = end_time - start_time
        return result
    except Exception as e:
        raise ParserError(f"Custom parser failed: {str(e)}") from e
```

### **3. Memory Management**
```python
def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
    # Check content length before processing
    max_length = self.config.get("max_content_length", 10_000_000)
    if len(html) > max_length:
        raise ParserError(f"Content too large: {len(html)} bytes")

    # Process content
    # ...
```

### **4. Type Hints**
```python
from typing import Optional, List
from backend.core.domain.parser import ParserResult, MetaData, Heading

def _extract_headings(self, html: str) -> List[Heading]:
    """Extract headings with proper type hints."""
    # Your implementation
    pass
```

### **5. Documentation**
```python
def parse(
    self,
    html: str,
    url: Optional[str] = None
) -> ParserResult:
    """
    Parse HTML content and return structured result.

    This method implements the core parsing logic for the custom parser,
    extracting title, text content, metadata, and structured elements.

    Args:
        html: HTML content to parse (required)
        url: Optional URL for link classification and error reporting

    Returns:
        ParserResult object containing all extracted content

    Raises:
        ParserError: If parsing fails due to invalid HTML or other errors

    Example:
        >>> parser = CustomParser()
        >>> result = parser.parse("<html><body><h1>Test</h1></body></html>")
        >>> print(result.title)
        'Test'
    """
    # Your implementation
    pass
```

## Verification Checklist

Before considering your parser implementation complete, verify:

- [ ] Implements all methods from `IParser` interface
- [ ] All methods have proper type hints
- [ ] Comprehensive docstrings for public methods
- [ ] Error handling with `ParserError` exceptions
- [ ] Performance metrics in `ParserResult`
- [ ] Unit tests covering all methods
- [ ] Integration tests with real HTML
- [ ] Code formatted with Black
- [ ] Linting passes with Ruff
- [ ] Type checking passes with MyPy
- [ ] Added to module exports
- [ ] Works with `ParserService`
- [ ] Handles edge cases (empty HTML, invalid HTML, etc.)

## Example Use Cases

### **Use Case 1: Industry-Specific Parser**
```python
class ECommerceParser(IParser):
    """Parser optimized for e-commerce websites."""

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # Extract product information, prices, reviews, etc.
        pass
```

### **Use Case 2: Performance-Optimized Parser**
```python
class FastParser(IParser):
    """High-performance parser using lxml."""

    def __init__(self):
        from lxml import html as lxml_html
        self.lxml = lxml_html

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # Use lxml for fast parsing
        pass
```

### **Use Case 3: Specialized Content Parser**
```python
class PDFContentParser(IParser):
    """Parser for PDF content converted to HTML."""

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # Handle PDF-specific HTML structure
        pass
```

## Conclusion

By following this guide, you can add new parser implementations to the AI Website Intelligence Platform without modifying any existing code. This follows the **Open/Closed Principle** and ensures that:

1. ✅ Existing parsers (`BeautifulSoupParser`, `TrafilaturaParser`) remain unchanged
2. ✅ New parsers integrate seamlessly with `ParserService`
3. ✅ All parsers follow the same `IParser` interface
4. ✅ Code remains maintainable and extensible
5. ✅ Testing and quality standards are maintained

The Parser Foundation architecture is designed for extensibility, and new parsers can be added as needed for specific use cases without compromising the existing codebase.