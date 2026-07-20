"""
Parser domain models for content extraction and analysis.

This module defines the core domain models for parsing HTML content,
including structured metadata and extracted elements.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, List, Dict
from urllib.parse import urlparse


class ContentType(str, Enum):
    """Types of content that can be extracted."""

    HTML = "html"
    TEXT = "text"
    METADATA = "metadata"
    HEADINGS = "headings"
    LINKS = "links"
    IMAGES = "images"
    SCRIPTS = "scripts"
    STYLESHEETS = "stylesheets"


@dataclass
class MetaData:
    """Extracted HTML metadata."""

    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    language: Optional[str] = None
    charset: Optional[str] = None
    viewport: Optional[str] = None
    robots: Optional[str] = None
    author: Optional[str] = None
    og_title: Optional[str] = None  # Open Graph title
    og_description: Optional[str] = None  # Open Graph description
    og_image: Optional[str] = None  # Open Graph image
    twitter_card: Optional[str] = None
    custom: Dict[str, str] = field(default_factory=dict)  # Custom meta tags


@dataclass
class Heading:
    """Extracted heading element."""

    level: int  # h1-h6
    text: str
    html_content: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Link:
    """Extracted link element."""

    url: str
    text: Optional[str] = None
    title: Optional[str] = None
    rel: Optional[str] = None  # Relationship type
    is_internal: bool = False
    is_nofollow: bool = False
    html_content: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Image:
    """Extracted image element."""

    src: str
    alt: Optional[str] = None
    title: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_internal: bool = False
    html_content: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Script:
    """Extracted script element."""

    src: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    async_flag: bool = False
    defer: bool = False
    html_content: Optional[str] = None


@dataclass
class Stylesheet:
    """Extracted stylesheet element."""

    href: Optional[str] = None
    content: Optional[str] = None
    media: Optional[str] = None
    is_internal: bool = False
    html_content: Optional[str] = None


@dataclass
class ParsingMetrics:
    """Metrics for parsing performance."""

    start_time: str
    end_time: str
    duration_ms: int
    bytes_processed: int = 0
    elements_extracted: int = 0
    parser_type: str = "unknown"


@dataclass
class ParserResult:
    """
    Result of HTML content parsing.

    Contains structured data extracted from HTML content including
    metadata, headings, links, images, scripts, and stylesheets.
    """

    # Input information
    url: str
    html_content: str

    # Basic extraction
    title: Optional[str] = None
    text_content: Optional[str] = None
    language: Optional[str] = None

    # Structured extraction
    metadata: MetaData = field(default_factory=MetaData)
    headings: List[Heading] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)
    scripts: List[Script] = field(default_factory=list)
    stylesheets: List[Stylesheet] = field(default_factory=list)

    # Performance and status
    success: bool = True
    error: Optional[str] = None
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: Optional[ParsingMetrics] = None

    # Additional data
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if not self.title and self.metadata.title:
            self.title = self.metadata.title

        # Determine if parsing was successful
        if self.error:
            self.success = False

    def get_internal_links(self) -> List[Link]:
        """Get all internal links."""
        return [link for link in self.links if link.is_internal]

    def get_external_links(self) -> List[Link]:
        """Get all external links."""
        return [link for link in self.links if not link.is_internal]

    def get_nofollow_links(self) -> List[Link]:
        """Get all nofollow links."""
        return [link for link in self.links if link.is_nofollow]

    def get_headings_by_level(self, level: int) -> List[Heading]:
        """Get all headings of a specific level."""
        return [heading for heading in self.headings if heading.level == level]

    def get_main_heading(self) -> Optional[Heading]:
        """Get the first H1 heading (main page heading)."""
        h1_headings = self.get_headings_by_level(1)
        return h1_headings[0] if h1_headings else None

    def get_internal_images(self) -> List[Image]:
        """Get all internal images."""
        return [img for img in self.images if img.is_internal]

    def get_external_images(self) -> List[Image]:
        """Get all external images."""
        return [img for img in self.images if not img.is_internal]

    def has_canonical_url(self) -> bool:
        """Check if canonical URL is present."""
        return self.metadata.canonical_url is not None

    def get_structured_content(self) -> Dict[str, Any]:
        """Get structured content as dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "description": self.metadata.description,
            "language": self.language,
            "headings_count": len(self.headings),
            "links_count": len(self.links),
            "internal_links_count": len(self.get_internal_links()),
            "external_links_count": len(self.get_external_links()),
            "images_count": len(self.images),
            "scripts_count": len(self.scripts),
            "stylesheets_count": len(self.stylesheets),
            "has_canonical_url": self.has_canonical_url(),
        }

    def get_text_summary(self, max_chars: int = 500) -> str:
        """Get a summary of the text content."""
        if not self.text_content:
            return ""

        text = self.text_content.strip()
        if len(text) <= max_chars:
            return text

        return text[: max_chars - 3] + "..."

    def validate(self) -> List[str]:
        """
        Validate the parsing result.

        Returns:
            List of validation warnings
        """
        warnings = []

        if not self.url:
            warnings.append("URL is missing")

        if not self.html_content:
            warnings.append("HTML content is missing")

        if not self.title:
            warnings.append("No title found")

        if not self.metadata.description:
            warnings.append("No meta description found")

        if not self.language:
            warnings.append("Language detection failed")

        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "text_content": self.text_content,
            "language": self.language,
            "metadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "keywords": self.metadata.keywords,
                "canonical_url": self.metadata.canonical_url,
                "language": self.metadata.language,
                "charset": self.metadata.charset,
                "author": self.metadata.author,
                "og_title": self.metadata.og_title,
                "og_description": self.metadata.og_description,
                "og_image": self.metadata.og_image,
                "custom": self.metadata.custom,
            },
            "headings": [
                {"level": h.level, "text": h.text, "attributes": h.attributes}
                for h in self.headings
            ],
            "links": [
                {
                    "url": l.url,
                    "text": l.text,
                    "title": l.title,
                    "rel": l.rel,
                    "is_internal": l.is_internal,
                    "is_nofollow": l.is_nofollow,
                }
                for l in self.links
            ],
            "images": [
                {
                    "src": i.src,
                    "alt": i.alt,
                    "title": i.title,
                    "width": i.width,
                    "height": i.height,
                    "is_internal": i.is_internal,
                }
                for i in self.images
            ],
            "scripts": [
                {
                    "src": s.src,
                    "type": s.type,
                    "async": s.async_flag,
                    "defer": s.defer,
                }
                for s in self.scripts
            ],
            "stylesheets": [
                {
                    "href": s.href,
                    "media": s.media,
                    "is_internal": s.is_internal,
                }
                for s in self.stylesheets
            ],
            "success": self.success,
            "error": self.error,
            "parsed_at": self.parsed_at,
            "metrics": (
                {
                    "duration_ms": self.metrics.duration_ms if self.metrics else 0,
                    "elements_extracted": self.metrics.elements_extracted if self.metrics else 0,
                }
                if self.metrics
                else None
            ),
            "structured_content": self.get_structured_content(),
        }


# Export for easy import
__all__ = [
    "ContentType",
    "MetaData",
    "Heading",
    "Link",
    "Image",
    "Script",
    "Stylesheet",
    "ParsingMetrics",
    "ParserResult",
]
