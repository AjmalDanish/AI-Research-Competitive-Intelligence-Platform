"""
Domain Entities Module

Business domain entities.

Purpose:
- Define business objects
- Encapsulate business rules
- Provide in-memory representations

Clean Architecture:
- Core layer (innermost)
- Pure business logic
- Framework-independent

This module will be populated in future milestones with entities like:
- Website
- Page
- Intelligence
- Technology
"""

"""
Domain Entities Module

Business domain entities.

Purpose:
- Define business objects
- Encapsulate business rules
- Provide in-memory representations

Clean Architecture:
- Core layer (innermost)
- Pure business logic
- Framework-independent

This module contains:
- crawler: Crawl result and metric entities
"""

from backend.core.domain.crawler import CrawlerConfig, CrawlMetrics, CrawlResult

# Export for easy import
__all__ = [
    "CrawlMetrics",
    "CrawlResult",
    "CrawlerConfig",
]
