"""
Whitespace Normalizer Implementation.

Normalizes whitespace in text content including:
- Standardizing line breaks
- Collapsing multiple spaces
- Trimming leading/trailing whitespace
- Normalizing tabs and other whitespace characters
"""

import re
import time
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class WhitespaceNormalizer(IContentProcessor):
    """
    Normalizes whitespace in text content.

    This processor handles various whitespace issues including:
    - Multiple consecutive spaces
    - Inconsistent line breaks
    - Leading/trailing whitespace
    - Tab characters
    - Non-breaking spaces
    """

    def __init__(self):
        """Initialize whitespace normalizer."""
        self.stage = ProcessingStage.WHITESPACE_NORMALIZATION

    def get_stage(self) -> ProcessingStage:
        """Return the processing stage."""
        return self.stage

    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Normalize whitespace in content.

        Args:
            content: Input content to normalize
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (normalized_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        normalized_content = content

        # Normalize line breaks
        if options.normalize_newlines:
            normalized_content = self._normalize_linebreaks(normalized_content)

        # Collapse multiple spaces
        if options.collapse_multiple_spaces:
            normalized_content = self._collapse_multiple_spaces(normalized_content)

        # Trim whitespace
        if options.trim_whitespace:
            normalized_content = self._trim_whitespace(normalized_content)

        # Update metadata
        metadata["whitespace_normalized"] = True
        metadata["whitespace_normalization_timestamp"] = time.time()

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["whitespace_normalized_count"] = context["metrics"].get("whitespace_normalized_count", 0) + 1

        return normalized_content, metadata

    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for whitespace normalization.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if content is too short after processing
        if len(content.strip()) < options.min_paragraph_length:
            errors.append(f"Content too short after whitespace normalization: {len(content.strip())} characters")

        return errors

    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for whitespace normalization.

        Args:
            input_length: Length of input content
            output_length: Length of output content
            duration_seconds: Processing duration

        Returns:
            Dictionary of processing metrics
        """
        reduction = input_length - output_length
        reduction_percentage = (reduction / input_length * 100) if input_length > 0 else 0

        return {
            "input_length": input_length,
            "output_length": output_length,
            "reduction": reduction,
            "reduction_percentage": reduction_percentage,
            "duration_seconds": duration_seconds,
            "characters_normalized": reduction,
        }

    def _normalize_linebreaks(self, content: str) -> str:
        """
        Normalize line breaks to standard format.

        Args:
            content: Content with potentially inconsistent line breaks

        Returns:
            Content with normalized line breaks
        """
        # Normalize Windows line breaks (\r\n) to Unix (\n)
        content = re.sub(r'\r\n', '\n', content)

        # Normalize Mac line breaks (\r) to Unix (\n)
        content = re.sub(r'\r', '\n', content)

        # Collapse multiple consecutive line breaks
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content

    def _collapse_multiple_spaces(self, content: str) -> str:
        """
        Collapse multiple consecutive spaces into single spaces.

        Args:
            content: Content with potentially multiple spaces

        Returns:
            Content with collapsed spaces
        """
        # Collapse multiple spaces within lines
        lines = content.split('\n')
        collapsed_lines = []

        for line in lines:
            # Collapse multiple spaces
            collapsed_line = re.sub(r' +', ' ', line)
            collapsed_lines.append(collapsed_line)

        return '\n'.join(collapsed_lines)

    def _trim_whitespace(self, content: str) -> str:
        """
        Trim leading and trailing whitespace from content.

        Args:
            content: Content with potential leading/trailing whitespace

        Returns:
            Content with trimmed whitespace
        """
        lines = content.split('\n')
        trimmed_lines = [line.strip() for line in lines]

        # Remove empty lines at the beginning
        while trimmed_lines and not trimmed_lines[0]:
            trimmed_lines.pop(0)

        # Remove empty lines at the end
        while trimmed_lines and not trimmed_lines[-1]:
            trimmed_lines.pop()

        return '\n'.join(trimmed_lines)

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for whitespace normalization.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Whitespace normalization is very fast: 0.0001 seconds per character
        return content_length * 0.0001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for whitespace normalization.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Low memory usage: 2x content size
        return content_length * 2