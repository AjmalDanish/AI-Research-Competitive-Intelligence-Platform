# Parser Module - Public API Documentation

## Overview

The Parser Module provides a Clean Architecture-based HTML parsing system with multiple parser implementations. This document describes the public API for developers who need to integrate with the parsing system.

## Module Structure

```
backend/parser/
├── __init__.py              # Public API exports
├── exceptions.py            # Parser-specific exceptions
├── parser_service.py        # Orchestration service
└── implementations/
    ├── __init__.py         # Parser implementations exports
    ├── beautifulsoup_parser.py  # BeautifulSoup4 implementation
    └── trafilatura_parser.py    # Trafilatura implementation

backend/core/
├── domain/
│   └── parser.py          # Domain models (ParserResult, MetaData, etc.)
└── interfaces/
    └── parser.py          # IParser interface definition
```

## Public API Exports

### **Main Entry Point**

```python
from backend.parser import (
    # Service
    ParserService,

    # Parsers
    BeautifulSoupParser,
    TrafilaturaParser,

    # Exceptions
    ParserError,
    ParserNotAvailableError,
    ParseTimeoutError,
    InvalidHTMLError,

    # Domain Models
    ParserResult,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
    ParsingMetrics,
)
```

### **Core Interface**

```python
from backend.core.interfaces import IParser
```

---

## Classes

### **ParserService**

The main orchestration service for HTML parsing operations.

#### **Constructor**

```python
def __init__(
    primary_parser: IParser,
    fallback_parser: Optional[IParser] = None,
    enable_fallback: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Parameters:**
- `primary_parser`: The main parser to use (required)
- `fallback_parser`: Backup parser if primary fails (optional)
- `enable_fallback`: Whether to use fallback parser on failure (default: `True`)
- `config`: Optional configuration dictionary for the service

**Example:**
```python
from backend.parser import ParserService, BeautifulSoupParser, TrafilaturaParser

# Create service with fallback
service = ParserService(
    primary_parser=BeautifulSoupParser(),
    fallback_parser=TrafilaturaParser(),
    enable_fallback=True
)

# Create service without fallback
service = ParserService(
    primary_parser=BeautifulSoupParser(),
    enable_fallback=False
)
```

#### **Methods**

##### **parse**

Parses HTML content using the configured parser strategy.

```python
def parse(
    html: str,
    url: Optional[str] = None,
    parser_type: Optional[str] = None
) -> ParserResult
```

**Parameters:**
- `html`: The HTML content to parse (required)
- `url`: Optional URL for link classification and error reporting
- `parser_type`: Optional parser type to force specific parser (`'beautifulsoup'`, `'trafilatura'`, or `None` for automatic selection)

**Returns:** `ParserResult` object with parsed content

**Raises:** `ParserError` if all parsers fail

**Example:**
```python
# Auto-select parser
result = service.parse(html, url="https://example.com")

# Force specific parser
result = service.parse(html, url="https://example.com", parser_type="beautifulsoup")
```

##### **parse_batch**

Parses multiple HTML documents in batch.

```python
def parse_batch(
    html_list: List[Tuple[str, Optional[str]]],
    show_progress: bool = False
) -> List[ParserResult]
```

**Parameters:**
- `html_list`: List of tuples `(html, url)` where `url` is optional
- `show_progress`: Whether to show progress for batch operations (default: `False`)

**Returns:** List of `ParserResult` objects in the same order as input

**Example:**
```python
html_list = [
    ("<html>...</html>", "https://example1.com"),
    ("<html>...</html>", "https://example2.com"),
]

results = service.parse_batch(html_list, show_progress=True)
```

##### **recommend_parser**

Recommends the best parser for given content characteristics.

```python
def recommend_parser(
    url: Optional[str] = None,
    content_type: Optional[str] = None
) -> str
```

**Parameters:**
- `url`: Optional URL to analyze for parser recommendation
- `content_type`: Optional content type string (e.g., `"text/html"`, `"article"`)

**Returns:** String indicating recommended parser (`'beautifulsoup'` or `'trafilatura'`)

**Example:**
```python
# Get recommendation for a URL
recommended = service.recommend_parser(url="https://news.example.com/article")
print(f"Recommended parser: {recommended}")

# Get recommendation by content type
recommended = service.recommend_parser(content_type="article")
```

##### **get_available_parsers**

Returns list of available parser types.

```python
def get_available_parsers() -> List[str]
```

**Returns:** List of parser type strings

**Example:**
```python
parsers = service.get_available_parsers()
print(f"Available parsers: {parsers}")  # ['beautifulsoup', 'trafilatura']
```

##### **get_metrics**

Returns parsing performance metrics.

```python
def get_metrics() -> Dict[str, Any]
```

**Returns:** Dictionary with parsing statistics:
- `total_parses`: Total number of parse operations
- `successful_parses`: Number of successful parses
- `failed_parses`: Number of failed parses
- `average_parse_time`: Average parsing time in seconds
- `parser_usage`: Dictionary of parser usage counts

**Example:**
```python
metrics = service.get_metrics()
print(f"Success rate: {metrics['successful_parses'] / metrics['total_parses']:.2%}")
```

##### **reset_metrics**

Resets parsing performance metrics.

```python
def reset_metrics() -> None
```

**Example:**
```python
service.reset_metrics()
```

---

### **BeautifulSoupParser**

HTML parser using BeautifulSoup4 for comprehensive DOM traversal and metadata extraction.

#### **Constructor**

```python
def __init__(
    config: Optional[BeautifulSoupConfig] = None,
    user_agent: Optional[str] = None
) -> None
```

**Parameters:**
- `config`: Optional configuration object (see BeautifulSoupConfig below)
- `user_agent`: Optional custom user agent string

**Example:**
```python
from backend.parser import BeautifulSoupParser
from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupConfig

config = BeautifulSoupConfig(
    max_content_length=10_000_000,
    timeout_seconds=30,
    extract_images=True,
    extract_scripts=True,
    extract_stylesheets=True
)

parser = BeautifulSoupParser(config=config)
```

#### **BeautifulSoupConfig**

Configuration class for BeautifulSoup parser.

```python
@dataclass
class BeautifulSoupConfig:
    max_content_length: int = 10_000_000  # Maximum HTML content size in bytes
    timeout_seconds: int = 30             # Parsing timeout
    extract_images: bool = True           # Whether to extract images
    extract_scripts: bool = True          # Whether to extract scripts
    extract_stylesheets: bool = True      # Whether to extract stylesheets
    min_image_width: int = 10             # Minimum image width to extract
    min_image_height: int = 10            # Minimum image height to extract
```

---

### **TrafilaturaParser**

Content-focused parser using Trafilatura for fast article extraction.

#### **Constructor**

```python
def __init__(
    config: Optional[TrafilaturaConfig] = None,
    user_agent: Optional[str] = None
) -> None
```

**Parameters:**
- `config`: Optional configuration object (see TrafilaturaConfig below)
- `user_agent`: Optional custom user agent string

**Example:**
```python
from backend.parser import TrafilaturaParser
from backend.parser.implementations.trafilatura_parser import TrafilaturaConfig

config = TrafilaturaConfig(
    max_content_length=5_000_000,
    timeout_seconds=30,
    extract_comments=False,
    extract_tables=True
)

parser = TrafilaturaParser(config=config)
```

#### **TrafilaturaConfig**

Configuration class for Trafilatura parser.

```python
@dataclass
class TrafilaturaConfig:
    max_content_length: int = 5_000_000   # Maximum HTML content size in bytes
    timeout_seconds: int = 30             # Parsing timeout
    extract_comments: bool = False        # Whether to extract comments
    extract_tables: bool = True           # Whether to extract tables
    extract_links: bool = True            # Whether to extract links
    include_formatting: bool = True       # Whether to include formatting in text
```

---

### **IParser Interface**

The base interface that all parser implementations must follow.

```python
class IParser(ABC):
    @abstractmethod
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        """Parse HTML content and return structured result."""
        pass

    @abstractmethod
    def extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        pass

    @abstractmethod
    def extract_text_content(self, html: str) -> str:
        """Extract main text content from HTML."""
        pass

    @abstractmethod
    def detect_language(self, html: str) -> Optional[str]:
        """Detect content language."""
        pass

    @abstractmethod
    def extract_metadata(self, html: str) -> MetaData:
        """Extract metadata from HTML."""
        pass
```

---

## Domain Models

### **ParserResult**

The main result object containing all parsed content.

```python
@dataclass
class ParserResult:
    url: str                              # Source URL
    title: str                             # Extracted title
    content: str                           # Full HTML content
    text_content: str                      # Cleaned text content
    metadata: MetaData                     # Structured metadata
    headings: List[Heading]                # Heading hierarchy (h1-h6)
    links: List[Link]                      # All links found
    images: List[Image]                    # All images found
    scripts: List[Script]                  # Script files found
    stylesheets: List[Stylesheet]          # Stylesheet files found
    metrics: ParsingMetrics                # Performance metrics

    def get_external_links(self) -> List[Link]:
        """Returns only external links."""

    def get_internal_links(self, base_url: Optional[str] = None) -> List[Link]:
        """Returns only internal links."""

    def get_headings_by_level(self, level: int) -> List[Heading]:
        """Returns headings by level (1-6)."""

    def get_images_by_size(self, min_width: int, min_height: int) -> List[Image]:
        """Returns images meeting minimum size requirements."""
```

### **MetaData**

Structured metadata extracted from HTML.

```python
@dataclass
class MetaData:
    title: str                             # Page title
    description: Optional[str]             # Meta description
    keywords: List[str]                    # Meta keywords
    canonical_url: Optional[str]           # Canonical URL
    og_data: Dict[str, str]                # Open Graph data
    twitter_data: Dict[str, str]           # Twitter card data
    author: Optional[str]                  # Author metadata
    publish_date: Optional[datetime]       # Publish date
    language: Optional[str]                # Content language
    content_type: Optional[str]            # Content type
```

### **Heading**

Heading element with level and position information.

```python
@dataclass
class Heading:
    level: int                             # Heading level (1-6)
    text: str                              # Heading text
    position: int                          # Position in document
```

### **Link**

Link element with classification.

```python
@dataclass
class Link:
    url: str                               # Link URL
    text: Optional[str]                    # Link text
    title: Optional[str]                   # Link title
    is_external: bool                      # Whether link is external
    is_nofollow: bool                      # Whether link has rel="nofollow"
    position: int                          # Position in document

    @classmethod
    def classify_link(cls, url: str, base_url: str) -> bool:
        """Classify link as internal or external."""
```

### **Image**

Image element with dimension information.

```python
@dataclass
class Image:
    url: str                               # Image URL
    alt_text: Optional[str]                # Alt text
    title: Optional[str]                   # Image title
    width: Optional[int]                   # Image width
    height: Optional[int]                  # Image height
    position: int                          # Position in document
```

### **Script**

Script element reference.

```python
@dataclass
class Script:
    url: Optional[str]                     # Script URL (if external)
    content: Optional[str]                 # Script content (if inline)
    type: Optional[str]                    # Script type
    is_async: bool                         # Whether script is async
    is_defer: bool                         # Whether script is defer
    position: int                          # Position in document
```

### **Stylesheet**

Stylesheet reference.

```python
@dataclass
class Stylesheet:
    url: str                               # Stylesheet URL
    media: Optional[str]                   # Media type
    title: Optional[str]                   # Stylesheet title
    position: int                          # Position in document
```

### **ParsingMetrics**

Performance tracking metrics.

```python
@dataclass
class ParsingMetrics:
    parse_duration_seconds: float          # Time taken to parse (seconds)
    content_length: int                    # Original content length (bytes)
    text_length: int                       # Extracted text length (bytes)
    heading_count: int                     # Number of headings found
    link_count: int                        # Number of links found
    image_count: int                       # Number of images found
    script_count: int                      # Number of scripts found
    stylesheet_count: int                  # Number of stylesheets found
    parser_used: str                       # Which parser was used
```

---

## Exceptions

### **ParserError**

Base exception for parser-related errors.

```python
class ParserError(Exception):
    """Base exception for parser errors."""
    pass
```

### **ParserNotAvailableError**

Raised when a requested parser is not available.

```python
class ParserNotAvailableError(ParserError):
    """Raised when a parser is not available."""
    pass
```

### **ParseTimeoutError**

Raised when parsing operation times out.

```python
class ParseTimeoutError(ParserError):
    """Raised when parsing times out."""
    pass
```

### **InvalidHTMLError**

Raised when HTML content is invalid or cannot be parsed.

```python
class InvalidHTMLError(ParserError):
    """Raised when HTML content is invalid."""
    pass
```

---

## Usage Examples

### **Basic Parsing**

```python
from backend.parser import ParserService, BeautifulSoupParser

# Create service
service = ParserService(
    primary_parser=BeautifulSoupParser()
)

# Parse HTML
html = "<html><head><title>Example</title></head><body><h1>Hello</h1></body></html>"
result = service.parse(html, url="https://example.com")

# Access results
print(f"Title: {result.title}")
print(f"Text Content: {result.text_content}")
print(f"Headings: {[h.text for h in result.headings]}")
```

### **Using Specific Parser**

```python
from backend.parser import ParserService, BeautifulSoupParser, TrafilaturaParser

# Create service with both parsers
service = ParserService(
    primary_parser=BeautifulSoupParser(),
    fallback_parser=TrafilaturaParser()
)

# Parse with automatic selection
result = service.parse(html, url="https://news.example.com/article")

# Parse with specific parser
result = service.parse(html, parser_type="trafilatura")
```

### **Batch Processing**

```python
from backend.parser import ParserService, BeautifulSoupParser

service = ParserService(primary_parser=BeautifulSoupParser())

html_list = [
    ("<html>...</html>", "https://example1.com"),
    ("<html>...</html>", "https://example2.com"),
    ("<html>...</html>", "https://example3.com"),
]

results = service.parse_batch(html_list, show_progress=True)

for i, result in enumerate(results):
    print(f"Page {i+1}: {result.title}")
```

### **Accessing Parsed Content**

```python
# Get all links
all_links = result.links

# Get only external links
external_links = result.get_external_links()

# Get only internal links
internal_links = result.get_internal_links(base_url="https://example.com")

# Get headings by level
h1_headings = result.get_headings_by_level(1)
h2_headings = result.get_headings_by_level(2)

# Get images by size
large_images = result.get_images_by_size(min_width=100, min_height=100)

# Access metadata
print(f"Description: {result.metadata.description}")
print(f"Keywords: {result.metadata.keywords}")
print(f"Author: {result.metadata.author}")

# Access performance metrics
print(f"Parse time: {result.metrics.parse_duration_seconds:.2f}s")
print(f"Links found: {result.metrics.link_count}")
print(f"Images found: {result.metrics.image_count}")
```

### **Error Handling**

```python
from backend.parser import ParserService, ParserError, BeautifulSoupParser

service = ParserService(primary_parser=BeautifulSoupParser())

try:
    result = service.parse(html, url="https://example.com")
except ParserNotAvailableError as e:
    print(f"Parser not available: {e}")
except ParseTimeoutError as e:
    print(f"Parsing timeout: {e}")
except InvalidHTMLError as e:
    print(f"Invalid HTML: {e}")
except ParserError as e:
    print(f"Parsing error: {e}")
```

### **Configuration**

```python
from backend.parser import ParserService, BeautifulSoupParser
from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupConfig

# Configure parser
config = BeautifulSoupConfig(
    max_content_length=20_000_000,  # 20MB max
    timeout_seconds=60,            # 60 second timeout
    extract_images=True,
    extract_scripts=True,
    extract_stylesheets=True
)

parser = BeautifulSoupParser(config=config)
service = ParserService(primary_parser=parser)
```

### **Metrics Collection**

```python
from backend.parser import ParserService, BeautifulSoupParser

service = ParserService(primary_parser=BeautifulSoupParser())

# Parse several documents
for html in html_documents:
    service.parse(html)

# Get performance metrics
metrics = service.get_metrics()
print(f"Total parses: {metrics['total_parses']}")
print(f"Success rate: {metrics['successful_parses'] / metrics['total_parses']:.2%}")
print(f"Average time: {metrics['average_parse_time']:.3f}s")
print(f"Parser usage: {metrics['parser_usage']}")

# Reset metrics if needed
service.reset_metrics()
```

---

## Integration Guidelines

### **With Crawler Module**

```python
from backend.crawler import CrawlerService, CrawlerConfig
from backend.parser import ParserService, BeautifulSoupParser

# Create crawler
crawler = CrawlerService(config=CrawlerConfig())

# Create parser
parser = ParserService(primary_parser=BeautifulSoupParser())

# Crawl and parse
crawl_result = crawler.crawl("https://example.com")
parse_result = parser.parse(
    crawl_result.html,
    url=crawl_result.url
)

print(f"URL: {parse_result.url}")
print(f"Title: {parse_result.title}")
print(f"Content: {parse_result.text_content}")
```

### **Custom Parser Implementation**

```python
from backend.core.interfaces import IParser
from backend.core.domain.parser import ParserResult, MetaData

class CustomParser(IParser):
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # Custom parsing logic
        pass

    def extract_title(self, html: str) -> Optional[str]:
        # Title extraction
        pass

    def extract_text_content(self, html: str) -> str:
        # Text content extraction
        pass

    def detect_language(self, html: str) -> Optional[str]:
        # Language detection
        pass

    def extract_metadata(self, html: str) -> MetaData:
        # Metadata extraction
        pass

# Use custom parser
from backend.parser import ParserService

service = ParserService(primary_parser=CustomParser())
result = service.parse(html, url="https://example.com")
```

---

## Best Practices

### **Parser Selection**

1. **Use BeautifulSoupParser** for:
   - General HTML parsing
   - Comprehensive metadata extraction
   - SEO analysis
   - Content mining

2. **Use TrafilaturaParser** for:
   - News article extraction
   - Blog post parsing
   - Content-focused applications
   - Fast processing needs

3. **Use automatic selection** when:
   - Content type is unknown
   - URL patterns are mixed
   - Performance is not critical

### **Error Handling**

- Always handle `ParserError` exceptions
- Implement appropriate fallback strategies
- Log parsing failures for debugging
- Consider retry mechanisms for transient failures

### **Performance**

- Use `parse_batch()` for multiple documents
- Enable appropriate parser configurations
- Monitor metrics for performance optimization
- Consider caching for repeated URLs

### **Memory Management**

- Be mindful of large HTML documents
- Use content length limits
- Process large batches in chunks
- Monitor memory usage in production

---

## API Versioning

Current version: `1.0.0`

**Stability:** Stable for production use

**Breaking Changes:**
- API changes will increment major version number
- Backwards compatible changes increment minor version number
- Bug fixes increment patch version number

---

## Support

For issues, questions, or contributions:
- Review the architecture documentation: `backend/docs/PARSER_ARCHITECTURE.md`
- Check extension guide: `backend/docs/PARSER_EXTENSION_GUIDE.md`
- Review test cases for usage examples: `backend/tests/unit/parser/`