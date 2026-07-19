"""
Custom Exceptions Module

Application-specific exceptions for better error handling.

Purpose:
- Provide custom exception types
- Enable structured error handling
- Support error categorization
- Facilitate debugging and monitoring

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure exception definitions
"""


class BaseApplicationException(Exception):
    """
    Base application exception.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        detail: str | None = None,
        status_code: int = 500,
    ):
        """
        Initialize base application exception.

        Args:
            message: Human-readable error message
            detail: Detailed error information
            status_code: HTTP status code
        """
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(BaseApplicationException):
    """
    Validation exception.

    Raised when input validation fails.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize validation exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=422,
        )


class NotFoundException(BaseApplicationException):
    """
    Not found exception.

    Raised when a resource is not found.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize not found exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=404,
        )


class ConflictException(BaseApplicationException):
    """
    Conflict exception.

    Raised when a conflict with existing data occurs.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize conflict exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=409,
        )


class DatabaseException(BaseApplicationException):
    """
    Database exception.

    Raised when database operations fail.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize database exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=500,
        )


class ConfigurationException(BaseApplicationException):
    """
    Configuration exception.

    Raised when configuration is invalid or missing.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize configuration exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=500,
        )


class ExternalServiceException(BaseApplicationException):
    """
    External service exception.

    Raised when external service calls fail.
    """

    def __init__(self, message: str, detail: str | None = None):
        """Initialize external service exception."""
        super().__init__(
            message=message,
            detail=detail,
            status_code=502,
        )


# Export for easy import
__all__ = [
    "BaseApplicationException",
    "ValidationException",
    "NotFoundException",
    "ConflictException",
    "DatabaseException",
    "ConfigurationException",
    "ExternalServiceException",
]
