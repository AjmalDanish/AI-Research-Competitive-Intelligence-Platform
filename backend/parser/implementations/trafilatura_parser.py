"""
Trafilatura-based HTML parser implementation.

This module provides a content-focused parser using Trafilatura for
efficient text extraction and content cleaning.
"""

from typing import Optional, Dict, Any

try:
    import trafilatura
    from trafilatura.settings import use_config
except ImportError:
    trafilatura = None  # type: ignore

from backend.core.interfaces.parser import IParser
from backend.core.domain.parser import (
    ParserResult,
    MetaData,
    ParsingMetrics,
)
from backend.config.logging import get_logger

logger = get_logger(__name__)


class TrafilaturaParser(IParser):
    """
    Trafilatura-based HTML parser implementation.

    Provides efficient text extraction and content cleaning
    using Trafilatura library.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize Trafilatura parser.

        Args:
            config: Optional Trafilatura configuration
        """
        self.config = config or use_config()
        self._validate_dependencies()

    def _validate_dependencies(self):
        """Validate that Trafilatura is installed."""
        if trafilatura is None:
            raise ImportError(
                "Trafilatura is required for TrafilaturaParser. "
                "Install with: poetry add trafilatura"
            )

    @property
    def parser_name(self) -> str:
        """Get the name of this parser implementation."""
        return "trafilatura"

    async def parse(
        self, html_content: str, url: str, options: Optional[Dict[str, Any]] = None
    ) -> ParserResult:
        """
        Parse HTML content and extract structured data.

        Args:
            html_content: Raw HTML content to parse
            url: Source URL of the content
            options: Optional parsing options

        Returns:
            ParserResult: Structured parsing result
        """
        if not html_content:
            return ParserResult(
                url=url,
                html_content=html_content,
                success=False,
                error="Empty HTML content provided",
            )

        try:
            # Extract text content using Trafilatura
            text_content = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=False,
                include_images=False,
                include_links=False,
                no_fallback=True,
                config=self.config,
            )

            # Extract metadata
            metadata_doc = trafilatura.metadata.extract_metadata(
                html_content, default_url=url, config=self.config
            )

            # Create result object
            result = ParserResult(
                url=url,
                html_content=html_content,
                text_content=text_content,
                language=metadata_doc.language if metadata_doc else None,
            )

            # Extract basic metadata
            result.metadata = MetaData(
                title=metadata_doc.title,
                author=metadata_doc.author,
                description=metadata_doc.description,
                canonical_url=metadata_doc.url,
                date=metadata_doc.date,
                language=metadata_doc.language,
            )

            # Update title
            if result.metadata.title:
                result.title = result.metadata.title

            # Create metrics
            result.metrics = ParsingMetrics(
                start_time=options.get("start_time", "") if options else "",
                end_time=options.get("end_time", "") if options else "",
                duration_ms=options.get("duration_ms", 0) if options else 0,
                bytes_processed=len(html_content.encode("utf-8")),
                elements_extracted=1,  # At least text content
                parser_type=self.parser_name,
            )

            # Validate result
            warnings = result.validate()
            if warnings:
                result.additional_data["validation_warnings"] = warnings

            # Add Trafilatura metadata
            result.additional_data["trafilatura_metadata"] = {
                "title": str(metadata_doc.title) if metadata_doc.title else "",
                "author": str(metadata_doc.author) if metadata_doc.author else "",
                "description": str(metadata_doc.description) if metadata_doc.description else "",
                "canonical_url": str(metadata_doc.url) if metadata_doc.url else "",
                "date": str(metadata_doc.date) if metadata_doc.date else "",
                "language": str(metadata_doc.language) if metadata_doc.language else "",
            }

            logger.info(
                f"Successfully parsed URL {url} with Trafilatura",
                title=result.title,
                text_length=len(text_content) if text_content else 0,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to parse HTML from {url} with Trafilatura", error=str(e))
            return ParserResult(
                url=url,
                html_content=html_content,
                success=False,
                error=f"Trafilatura parsing failed: {str(e)}",
            )

    def can_parse(self, html_content: str) -> bool:
        """
        Check if this parser can handle the given HTML content.

        Args:
            html_content: HTML content to check

        Returns:
            bool: True if parser can handle this content
        """
        if not html_content:
            return False

        # Trafilatura can handle most HTML content
        # It's especially good for article and news content
        return True

    def extract_title(self, html_content: str) -> Optional[str]:
        """
        Extract page title from HTML content.

        Args:
            html_content: HTML content to extract title from

        Returns:
            Optional[str]: Page title or None if not found
        """
        try:
            metadata_dict = trafilatura.metadata.extract_metadata(
                html_content, default_url="", config=self.config
            )
            return metadata_dict.get("title")
        except Exception as e:
            logger.error(f"Failed to extract title with Trafilatura", error=str(e))
            return None

    def extract_text_content(self, html_content: str) -> str:
        """
        Extract clean text content from HTML.

        Args:
            html_content: HTML content to extract text from

        Returns:
            str: Clean text content
        """
        try:
            text_content = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=False,
                include_images=False,
                include_links=False,
                no_fallback=True,
                config=self.config,
            )
            return text_content if text_content else ""
        except Exception as e:
            logger.error(f"Failed to extract text with Trafilatura", error=str(e))
            return ""

    def detect_language(self, html_content: str) -> Optional[str]:
        """
        Detect the language of the content.

        Args:
            html_content: HTML content to analyze

        Returns:
            Optional[str]: Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            metadata_dict = trafilatura.metadata.extract_metadata(
                html_content, default_url="", config=self.config
            )
            return metadata_dict.get("language")
        except Exception as e:
            logger.error(f"Failed to detect language with Trafilatura", error=str(e))
            return None

    def extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract HTML metadata (title, description, etc.).

        Args:
            html_content: HTML content to extract metadata from

        Returns:
            Dict[str, Any]: Extracted metadata
        """
        try:
            metadata_doc = trafilatura.metadata.extract_metadata(
                html_content, default_url="", config=self.config
            )

            # Convert Document object to dictionary
            metadata_dict = {
                "title": str(metadata_doc.title) if metadata_doc.title else "",
                "author": str(metadata_doc.author) if metadata_doc.author else "",
                "description": str(metadata_doc.description) if metadata_doc.description else "",
                "canonical_url": str(metadata_doc.url) if metadata_doc.url else "",
                "date": str(metadata_doc.date) if metadata_doc.date else "",
                "language": str(metadata_doc.language) if metadata_doc.language else "",
            }

            return metadata_dict

        except Exception as e:
            logger.error(f"Failed to extract metadata with Trafilatura", error=str(e))
            return {}


# Export for easy import
__all__ = [
    "TrafilaturaParser",
]
