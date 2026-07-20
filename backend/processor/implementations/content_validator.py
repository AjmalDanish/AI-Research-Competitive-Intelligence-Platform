"""
Content Validator Implementation.

Validates processed content including:
- Content length validation
- Structure validation
- Consistency validation
- Quality validation
"""

from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class ContentValidator(IContentProcessor):
    """
    Validates processed content.

    This processor handles:
    - Content length validation
    - Structure validation
    - Consistency validation
    - Quality validation
    """

    def __init__(self):
        """Initialize content validator."""
        self.stage = ProcessingStage.VALIDATION

    def get_stage(self) -> ProcessingStage:
        """Return the processing stage."""
        return self.stage

    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any],
    ) -> tuple[str, Dict[str, Any]]:
        """
        Validate processed content.

        Args:
            content: Input content to validate
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (validated_content, updated_metadata)
        """
        validation_errors = []
        validation_warnings = []

        # Content length validation
        if not self._validate_content_length(content, options):
            validation_errors.append(
                f"Content length {len(content)} below minimum {options.minimum_content_length}"
            )

        # Empty content validation
        if not self._validate_non_empty(content, options):
            if options.allow_empty_content:
                validation_warnings.append(
                    "Content is empty but allowed by configuration"
                )
            else:
                validation_errors.append("Content is empty and not allowed")

        # Quality validation
        quality_errors = self._validate_content_quality(content, options)
        validation_errors.extend(quality_errors)

        # Structure validation
        structure_errors = self._validate_content_structure(content, options)
        validation_errors.extend(structure_errors)

        # Consistency validation
        consistency_errors = self._validate_content_consistency(content, metadata)
        validation_errors.extend(consistency_errors)

        # Update metadata with validation results
        metadata["validation_passed"] = len(validation_errors) == 0
        metadata["validation_errors"] = validation_errors
        metadata["validation_warnings"] = validation_warnings
        metadata["validation_timestamp"] = context.get("timestamp")

        # Update context metrics
        context.setdefault("metrics", {})
        context["metrics"]["validation_errors"] = len(validation_errors)
        context["metrics"]["validation_warnings"] = len(validation_warnings)

        # Raise error if strict validation and errors found
        if options.strict_validation and validation_errors:
            from backend.processor.exceptions import ProcessingValidationError

            raise ProcessingValidationError(validation_errors, "ContentValidation")

        return content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content without applying strict validation.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate configuration options
        if options.minimum_content_length < 0:
            errors.append("Minimum content length cannot be negative")

        if options.strict_validation and not options.allow_empty_content:
            errors.append("Strict validation with empty content disallowed")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for content validation.

        Args:
            input_length: Length of input content
            output_length: Length of output content
            duration_seconds: Processing duration

        Returns:
            Dictionary of processing metrics
        """
        return {
            "input_length": input_length,
            "output_length": output_length,
            "duration_seconds": duration_seconds,
            "validation_checks_performed": 4,  # Fixed number of validation checks
        }

    def _validate_content_length(
        self, content: str, options: ProcessingOptions
    ) -> bool:
        """
        Validate content length requirements.

        Args:
            content: Content to validate
            options: Processing configuration options

        Returns:
            True if content length is valid
        """
        return len(content.strip()) >= options.minimum_content_length

    def _validate_non_empty(self, content: str, options: ProcessingOptions) -> bool:
        """
        Validate that content is not empty.

        Args:
            content: Content to validate
            options: Processing configuration options

        Returns:
            True if content is non-empty or allowed to be empty
        """
        if options.allow_empty_content:
            return True

        return len(content.strip()) > 0

    def _validate_content_quality(
        self, content: str, options: ProcessingOptions
    ) -> List[str]:
        """
        Validate content quality.

        Args:
            content: Content to validate
            options: Processing configuration options

        Returns:
            List of quality validation errors
        """
        errors = []

        # Check for excessive whitespace
        if content.count("    ") > len(content) // 10:
            errors.append("Excessive tab characters detected")

        # Check for excessive consecutive line breaks
        if content.count("\n\n\n") > 3:
            errors.append("Excessive consecutive line breaks")

        # Check for very short content
        if len(content.strip()) < 10:
            errors.append("Content too short for meaningful processing")

        return errors

    def _validate_content_structure(
        self, content: str, options: ProcessingOptions
    ) -> List[str]:
        """
        Validate content structure.

        Args:
            content: Content to validate
            options: Processing configuration options

        Returns:
            List of structure validation errors
        """
        errors = []

        # Check for balanced quotes
        if content.count('"') % 2 != 0:
            errors.append("Unbalanced double quotes")

        if content.count("'") % 2 != 0:
            errors.append("Unbalanced single quotes")

        # Check for unusual patterns
        if "<<" in content or ">>" in content:
            errors.append("Unusual character patterns detected")

        return errors

    def _validate_content_consistency(
        self, content: str, metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Validate content consistency with metadata.

        Args:
            content: Content to validate
            metadata: Content metadata

        Returns:
            List of consistency validation errors
        """
        errors = []

        # Check if title matches content
        if "title" in metadata and metadata["title"]:
            title = metadata["title"].strip().lower()
            if title and title not in content.lower()[:200]:
                errors.append("Title not found in first 200 characters of content")

        # Check language consistency
        if "language" in metadata and metadata["language"]:
            # Simple check - would need more sophisticated analysis
            language = metadata["language"].lower()
            if language not in ["en", "es", "fr", "de", "it", "pt", "nl"]:
                errors.append(f"Language '{language}' not commonly supported")

        return errors

    def estimate_processing_time(
        self, content_length: int, options: ProcessingOptions
    ) -> float:
        """
        Estimate processing time for content validation.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Validation is very fast: 0.0001 seconds per character
        return content_length * 0.0001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for content validation.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Very low memory usage: 1.1x content size
        return int(content_length * 1.1)
