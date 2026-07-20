"""
Interfaces Module

Interfaces for crawler and parser modules.

Clean Architecture:
- Core layer (interfaces)
- No implementation details
- Pure interface definitions
"""

from backend.core.interfaces.crawler import ICrawler
from backend.core.interfaces.parser import IParser

# Export for easy import
__all__ = [
    "ICrawler",
    "IParser",
]
