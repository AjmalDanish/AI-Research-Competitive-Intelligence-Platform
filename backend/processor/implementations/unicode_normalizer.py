"""
Unicode Normalizer Implementation.

Normalizes Unicode content including:
- Standardizing Unicode forms (NFC, NFD, NFKC, NFKD)
- Normalizing quotes and dashes
- Handling special characters
- Removing invisible Unicode characters
"""

import re
import unicodedata
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class UnicodeNormalizer(IContentProcessor):
    """
    Normalizes Unicode content.

    This processor handles Unicode normalization including:
    - Unicode form normalization (NFC, NFD, NFKC, NFKD)
    - Quote character normalization
    - Dash character normalization
    - Removal of problematic Unicode characters
    """

    def __init__(self):
        """Initialize Unicode normalizer."""
        self.stage = ProcessingStage.UNICODE_NORMALIZATION

        # Character mappings for normalization
        self.quote_mappings = {
            '"': '"',  # Left and right double quotes to standard
            '"': '"',
            ''': "'",  # Left and right single quotes to standard
            ''': "'",
            '„': '"',  # Low double quotes
            "‚": "'",  # Low single quotes
            '«': '"',  # Angle quotes
            '»': '"',
            '‹': "'",
            '›': "'",
        }

        self.dash_mappings = {
            '–': '-',  # En dash
            '—': '--',  # Em dash
            '―': '--',  # Horizontal bar
        }

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
        Normalize Unicode content.

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

        # Apply Unicode form normalization
        try:
            normalized_content = unicodedata.normalize(
                options.unicode_form,
                normalized_content
            )
        except (ValueError, TypeError) as e:
            # Fall back to NFC if invalid form
            normalized_content = unicodedata.normalize('NFC', normalized_content)

        # Normalize quotes if enabled
        if options.normalize_quotes:
            normalized_content = self._normalize_quotes(normalized_content)

        # Normalize dashes if enabled
        if options.normalize_dashes:
            normalized_content = self._normalize_dashes(normalized_content)

        # Remove problematic invisible characters
        normalized_content = self._remove_invisible_characters(normalized_content)

        # Update metadata
        metadata["unicode_normalized"] = True
        metadata["unicode_form_used"] = options.unicode_form

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["unicode_normalized_count"] = context["metrics"].get("unicode_normalized_count", 0) + 1

        return normalized_content, metadata

    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for Unicode normalization.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate Unicode form option
        valid_forms = ['NFC', 'NFD', 'NFKC', 'NFKD']
        if options.unicode_form not in valid_forms:
            errors.append(f"Invalid Unicode form: {options.unicode_form}")

        # Check for problematic Unicode sequences
        try:
            content.encode('utf-8')
        except UnicodeEncodeError as e:
            errors.append(f"Content contains non-UTF-8 encodable characters: {e}")

        return errors

    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for Unicode normalization.

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
            "characters_normalized": input_length,
            "unicode_form_applied": "NFC",  # Will be updated in actual processing
        }

    def _normalize_quotes(self, content: str) -> str:
        """
        Normalize quote characters to standard forms.

        Args:
            content: Content with potentially non-standard quotes

        Returns:
            Content with normalized quotes
        """
        normalized_content = content

        for non_standard, standard in self.quote_mappings.items():
            normalized_content = normalized_content.replace(non_standard, standard)

        return normalized_content

    def _normalize_dashes(self, content: str) -> str:
        """
        Normalize dash characters to standard forms.

        Args:
            content: Content with potentially non-standard dashes

        Returns:
            Content with normalized dashes
        """
        normalized_content = content

        for non_standard, standard in self.dash_mappings.items():
            normalized_content = normalized_content.replace(non_standard, standard)

        return normalized_content

    def _remove_invisible_characters(self, content: str) -> str:
        """
        Remove problematic invisible Unicode characters.

        Args:
            content: Content with potentially invisible characters

        Returns:
            Content with invisible characters removed
        """
        # Remove zero-width characters
        invisible_chars = [
            '\u200B',  # Zero-width space
            '\u200C',  # Zero-width non-joiner
            '\u200D',  # Zero-width joiner
            '\uFEFF',  # Zero-width no-break space
            '\u00AD',  # Soft hyphen
        ]

        normalized_content = content

        for char in invisible_chars:
            normalized_content = normalized_content.replace(char, '')

        return normalized_content

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for Unicode normalization.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Unicode normalization is moderately fast: 0.0005 seconds per character
        return content_length * 0.0005

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for Unicode normalization.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 4x content size due to Unicode processing
        return content_length * 4