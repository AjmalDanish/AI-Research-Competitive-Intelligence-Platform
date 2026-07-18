"""
URL Validators Module

URL validation and normalization components.

This module contains all URL-related validation and normalization code:

- url_validator: URL validation and accessibility checking
- url_normalizer: URL normalization utilities

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure validation logic
"""

from backend.crawler.validators.url_normalizer import URLNormalizer
from backend.crawler.validators.url_validator import URLValidator

# Export for easy import
__all__ = [
    "URLValidator",
    "URLNormalizer",
]
