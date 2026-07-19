"""
Logging configuration and utilities.

This module sets up structured logging for the application with
console and file handlers.
"""

import logging
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging(
    name: Optional[str] = None, log_level: Optional[str] = None, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        name: Logger name (default: root logger)
        log_level: Log level (default: from settings)
        log_file: Log file path (default: from settings)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Get log level from settings or parameter
    level = (log_level or settings.LOG_LEVEL).upper()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    log_file_path = log_file or settings.LOG_FILE
    if log_file_path:
        # Create log directory if it doesn't exist
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class that provides logging functionality.

    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("This is a log message")
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


# Application logger
app_logger = setup_logging("aicp")
