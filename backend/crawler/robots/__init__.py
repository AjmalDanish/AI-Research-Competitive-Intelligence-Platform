"""
Robots Module

Robots.txt handling components.

This module contains robots.txt parsing and access control:

- robots_checker: Main robots.txt checker

Clean Architecture:
- Infrastructure layer
- robots.txt handling
- Access control
"""

from backend.crawler.robots.robots_checker import RobotsChecker

# Export for easy import
__all__ = [
    "RobotsChecker",
]
