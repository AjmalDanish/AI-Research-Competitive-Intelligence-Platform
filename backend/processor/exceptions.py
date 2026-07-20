"""
Content Processor exceptions.

This module defines all custom exceptions for the content processing module.
"""


class ProcessorError(Exception):
    """Base exception for processor errors."""

    def __init__(self, message: str, stage: str = None):
        """
        Initialize processor error.

        Args:
            message: Error message
            stage: Optional processing stage where error occurred
        """
        self.stage = stage
        super().__init__(f"{stage}: {message}" if stage else message)


class ProcessorNotAvailableError(ProcessorError):
    """Raised when a requested processor is not available."""

    def __init__(self, processor_name: str):
        """
        Initialize processor not available error.

        Args:
            processor_name: Name of the requested processor
        """
        self.processor_name = processor_name
        super().__init__(f"Processor '{processor_name}' is not available", "ProcessorAvailability")


class ProcessingTimeoutError(ProcessorError):
    """Raised when processing operation times out."""

    def __init__(self, timeout_seconds: float, stage: str = None):
        """
        Initialize processing timeout error.

        Args:
            timeout_seconds: Timeout duration in seconds
            stage: Optional processing stage that timed out
        """
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Processing timed out after {timeout_seconds} seconds",
            stage or "Processing"
        )


class ProcessingValidationError(ProcessorError):
    """Raised when content validation fails."""

    def __init__(self, validation_errors: list, stage: str = "Validation"):
        """
        Initialize processing validation error.

        Args:
            validation_errors: List of validation error messages
            stage: Processing stage where validation failed
        """
        self.validation_errors = validation_errors
        super().__init__(
            f"Content validation failed with {len(validation_errors)} errors",
            stage
        )


class ContentStructureError(ProcessorError):
    """Raised when content structure is invalid."""

    def __init__(self, message: str, stage: str = "StructureAnalysis"):
        """
        Initialize content structure error.

        Args:
            message: Error message describing structure issue
            stage: Processing stage that detected the structure error
        """
        super().__init__(message, stage)


class TextNormalizationError(ProcessorError):
    """Raised when text normalization fails."""

    def __init__(self, message: str, stage: str = "TextNormalization"):
        """
        Initialize text normalization error.

        Args:
            message: Error message describing normalization failure
            stage: Processing stage that failed normalization
        """
        super().__init__(message, stage)


class DuplicateDetectionError(ProcessorError):
    """Raised when duplicate detection fails."""

    def __init__(self, message: str, stage: str = "DuplicateDetection"):
        """
        Initialize duplicate detection error.

        Args:
            message: Error message describing detection failure
            stage: Processing stage that failed detection
        """
        super().__init__(message, stage)