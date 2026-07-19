"""
Logger Utility

Helper functions for logging.

Purpose:
- Provide convenient logging functions
- Support structured logging
- Enable context-aware logging

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure logging utilities
"""

from backend.config.logging import get_logger as _get_logger


def get_logger(name: str):
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return _get_logger(name)


# Export for easy import
__all__ = ["get_logger"]
