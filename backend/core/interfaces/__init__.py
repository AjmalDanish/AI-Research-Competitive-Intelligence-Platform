"""
Crawler Interface Module

Interfaces for the crawler module.

Clean Architecture:
- Core layer (interfaces)
- No implementation details
- Pure interface definitions
"""

from backend.core.interfaces.crawler import ICrawler

# Export for easy import
__all__ = [
    "ICrawler",
]
