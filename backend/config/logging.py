"""
Logging Configuration Module

Structured logging setup with JSON and text format support.

Purpose:
- Centralize logging configuration
- Provide structured logging
- Support both JSON and text formats
- Enable module-specific loggers
- Production-ready logging

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure logging configuration
"""

import logging
import sys
from datetime import datetime
from typing import Any
from typing import Literal

from backend.config.settings import get_settings


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Formats log records as JSON objects for production environments.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        import json
        
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "message",
                "asctime", "getMessage"
            }:
                log_obj[key] = value
        
        return json.dumps(log_obj)


class TextFormatter(logging.Formatter):
    """
    Text formatter for human-readable logging.
    
    Formats log records as readable text for development environments.
    """
    
    def __init__(self) -> None:
        """Initialize text formatter with custom format."""
        format_str = (
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        super().__init__(format_str, datefmt=date_format)


class LoggingConfig:
    """
    Centralized logging configuration.
    
    Features:
    - Structured JSON logging (production)
    - Human-readable text logging (development)
    - Module-specific log levels
    - File rotation and retention
    - Console and file output
    """
    
    def __init__(self):
        """Initialize logging configuration."""
        self.settings = get_settings()
        self._configure_root_logger()
    
    def _configure_root_logger(self) -> None:
        """Configure root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.settings.LOG_LEVEL))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.settings.LOG_LEVEL))
        
        if self.settings.LOG_FORMAT == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(TextFormatter())
        
        root_logger.addHandler(console_handler)
        
        # File handler (if configured)
        if self.settings.LOG_FILE:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                filename=self.settings.LOG_FILE,
                maxBytes=self._parse_size(self.settings.LOG_ROTATION),
                backupCount=self._parse_retention(self.settings.LOG_RETENTION),
            )
            file_handler.setLevel(getattr(logging, self.settings.LOG_LEVEL))
            
            if self.settings.LOG_FORMAT == "json":
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(TextFormatter())
            
            root_logger.addHandler(file_handler)
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parse size string like '10 MB' to bytes."""
        size_str = size_str.upper().strip()
        if "MB" in size_str:
            return int(size_str.replace("MB", "").strip()) * 1024 * 1024
        elif "KB" in size_str:
            return int(size_str.replace("KB", "").strip()) * 1024
        elif "GB" in size_str:
            return int(size_str.replace("GB", "").strip()) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    @staticmethod
    def _parse_retention(retention_str: str) -> int:
        """Parse retention string like '30 days' to number of backups."""
        retention_str = retention_str.lower().strip()
        if "days" in retention_str:
            return int(retention_str.replace("days", "").strip())
        elif "weeks" in retention_str:
            return int(retention_str.replace("weeks", "").strip()) * 7
        else:
            return int(retention_str)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


# Module-level convenience function
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return LoggingConfig.get_logger(name)


# Initialize logging
config = LoggingConfig()

# Module-level logger
logger = config.get_logger(__name__)


# Export for easy import
__all__ = ["LoggingConfig", "logger", "get_logger"]