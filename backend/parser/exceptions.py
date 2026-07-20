"""
Parser exceptions for handling parsing errors.

This module defines custom exceptions for parser-related errors
following Clean Architecture principles.
"""

from typing import Optional


class ParserException(Exception):
    """Base exception for parser errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize parser exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class EmptyContentError(ParserException):
    """Exception raised when empty content is provided for parsing."""

    def __init__(self, url: Optional[str] = None):
        """
        Initialize empty content error.

        Args:
            url: URL that had empty content
        """
        message = f"Empty HTML content provided"
        if url:
            message = f"Empty HTML content provided for {url}"
        super().__init__(message)


class InvalidHTMLError(ParserException):
    """Exception raised when invalid HTML content is provided."""

    def __init__(self, message: str = "Invalid HTML content provided"):
        """
        Initialize invalid HTML error.

        Args:
            message: Error message
        """
        super().__init__(message)


class ParserTimeoutError(ParserException):
    """Exception raised when parsing exceeds time limit."""

    def __init__(self, message: str = "Parser timeout exceeded"):
        """
        Initialize parser timeout error.

        Args:
            message: Error message
        """
        super().__init__(message)


class UnsupportedFormatError(ParserException):
    """Exception raised when content format is not supported."""

    def __init__(self, content_type: str, message: str = "Unsupported content format"):
        """
        Initialize unsupported format error.

        Args:
            content_type: Unsupported content type
            message: Error message
        """
        self.content_type = content_type
        super().__init__(f"{message}: {content_type}")


class ParserNotFoundError(ParserException):
    """Exception raised when requested parser is not available."""

    def __init__(self, parser_type: str):
        """
        Initialize parser not found error.

        Args:
            parser_type: Type of parser that was not found
        """
        self.parser_type = parser_type
        super().__init__(f"Parser '{parser_type}' not found or not available")


class ExtractionError(ParserException):
    """Exception raised when content extraction fails."""

    def __init__(self, element_type: str, message: str = "Content extraction failed"):
        """
        Initialize extraction error.

        Args:
            element_type: Type of element that failed extraction
            message: Error message
        """
        self.element_type = element_type
        super().__init__(f"{message}: {element_type}")


# Export for easy import
__all__ = [
    "ParserException",
    "EmptyContentError",
    "InvalidHTMLError",
    "ParserTimeoutError",
    "UnsupportedFormatError",
    "ParserNotFoundError",
    "ExtractionError",
]
