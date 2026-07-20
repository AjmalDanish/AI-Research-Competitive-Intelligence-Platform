"""
Parser interface for HTML content extraction.

This module defines the contract for HTML parsers following the
Interface Segregation Principle from Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from backend.core.domain.parser import ParserResult


class IParser(ABC):
    """
    Interface for HTML content parsers.

    This interface defines the contract that all parser implementations
    must follow, ensuring polymorphism and interchangeable parser strategies.
    """

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """Get the name of this parser implementation."""
        pass

    @abstractmethod
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

        Raises:
            ParserException: If parsing fails
        """
        pass

    @abstractmethod
    def can_parse(self, html_content: str) -> bool:
        """
        Check if this parser can handle the given HTML content.

        Args:
            html_content: HTML content to check

        Returns:
            bool: True if parser can handle this content
        """
        pass

    @abstractmethod
    def extract_title(self, html_content: str) -> Optional[str]:
        """
        Extract page title from HTML content.

        Args:
            html_content: HTML content to extract title from

        Returns:
            Optional[str]: Page title or None if not found
        """
        pass

    @abstractmethod
    def extract_text_content(self, html_content: str) -> str:
        """
        Extract clean text content from HTML.

        Args:
            html_content: HTML content to extract text from

        Returns:
            str: Clean text content
        """
        pass

    @abstractmethod
    def detect_language(self, html_content: str) -> Optional[str]:
        """
        Detect the language of the content.

        Args:
            html_content: HTML content to analyze

        Returns:
            Optional[str]: Language code (e.g., 'en', 'es', 'fr')
        """
        pass

    @abstractmethod
    def extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract HTML metadata (title, description, etc.).

        Args:
            html_content: HTML content to extract metadata from

        Returns:
            Dict[str, Any]: Extracted metadata
        """
        pass

    def normalize_url(self, url: str, base_url: str) -> str:
        """
        Normalize a URL relative to a base URL.

        Args:
            url: URL to normalize
            base_url: Base URL for resolution

        Returns:
            str: Normalized absolute URL
        """
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme and parsed_url.netloc:
                return url  # Already absolute

            parsed_base = urlparse(base_url)
            scheme = parsed_base.scheme or "https"
            netloc = parsed_base.netloc

            if url.startswith("//"):
                return f"{scheme}:{url}"
            elif url.startswith("/"):
                return f"{scheme}://{netloc}{url}"
            else:
                path = parsed_base.path.rsplit("/", 1)[0]
                return f"{scheme}://{netloc}/{path}/{url}"
        except Exception:
            return url

    def is_internal_url(self, url: str, base_url: str) -> bool:
        """
        Check if a URL is internal to the base domain.

        Args:
            url: URL to check
            base_url: Base URL for comparison

        Returns:
            bool: True if URL is internal to the base domain
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            return parsed_url.netloc == parsed_base.netloc
        except Exception:
            return False

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Text to clean

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        cleaned = " ".join(text.split())

        # Remove common artifacts
        artifacts = ["\\r", "\\n", "\\t"]
        for artifact in artifacts:
            cleaned = cleaned.replace(artifact, " ")

        # Clean up remaining whitespace
        cleaned = " ".join(cleaned.split())

        return cleaned


# Export for easy import
__all__ = [
    "IParser",
]
