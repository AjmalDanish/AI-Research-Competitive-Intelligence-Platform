"""
Parser module for HTML content extraction and analysis.

This module provides parsing capabilities using BeautifulSoup4
and Trafilatura for comprehensive HTML content extraction.
"""

from backend.parser.parser_service import ParserService, parser_service, get_parser_service
from backend.parser.exceptions import (
    ParserException,
    EmptyContentError,
    InvalidHTMLError,
    ParserTimeoutError,
    UnsupportedFormatError,
    ParserNotFoundError,
    ExtractionError,
)
from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupParser
from backend.parser.implementations.trafilatura_parser import TrafilaturaParser

# Export for easy import
__all__ = [
    # Service
    "ParserService",
    "parser_service",
    "get_parser_service",
    # Exceptions
    "ParserException",
    "EmptyContentError",
    "InvalidHTMLError",
    "ParserTimeoutError",
    "UnsupportedFormatError",
    "ParserNotFoundError",
    "ExtractionError",
    # Implementations
    "BeautifulSoupParser",
    "TrafilaturaParser",
]
