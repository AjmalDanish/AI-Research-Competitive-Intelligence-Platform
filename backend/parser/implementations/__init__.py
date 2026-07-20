"""
Parser implementations module.

Contains concrete implementations of the IParser interface:
- BeautifulSoupParser: DOM-based comprehensive extraction
- TrafilaturaParser: Content-focused efficient extraction
"""

from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupParser
from backend.parser.implementations.trafilatura_parser import TrafilaturaParser

# Export for easy import
__all__ = [
    "BeautifulSoupParser",
    "TrafilaturaParser",
]
