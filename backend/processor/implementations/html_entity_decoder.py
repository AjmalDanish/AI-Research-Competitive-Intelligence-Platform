"""
HTML Entity Decoder Implementation.

Decodes HTML entities including:
- Named entities (&amp;, &lt;, &gt;, etc.)
- Numeric entities (&#123;, &#xABC;)
- Special character entities
"""

import html
import re
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class HTMLEntityDecoder(IContentProcessor):
    """
    Decodes HTML entities in content.

    This processor handles:
    - Named HTML entities
    - Decimal numeric entities
    - Hexadecimal numeric entities
    - Custom entity handling
    """

    def __init__(self):
        """Initialize HTML entity decoder."""
        self.stage = ProcessingStage.HTML_ENTITY_DECODING

        # Common HTML entities that might need special handling
        self.common_entities = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&apos;": "'",
            "&nbsp;": " ",
            "&copy;": "©",
            "&reg;": "®",
            "&trade;": "™",
        }

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
        Decode HTML entities in content.

        Args:
            content: Input content with HTML entities
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (decoded_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        # Count entities before decoding
        entity_count = self._count_entities(content)

        # Use Python's html.unescape for standard decoding
        decoded_content = html.unescape(content)

        # Handle any remaining entities
        decoded_content = self._handle_remaining_entities(decoded_content)

        # Update metadata
        metadata["html_entities_decoded"] = True
        metadata["html_entity_count"] = entity_count

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["html_entities_decoded"] = (
            context["metrics"].get("html_entities_decoded", 0) + entity_count
        )

        return decoded_content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for HTML entity decoding.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check for malformed entities
        malformed_entities = self._find_malformed_entities(content)
        if malformed_entities:
            errors.append(f"Found {len(malformed_entities)} malformed HTML entities")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for HTML entity decoding.

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
            "entities_decoded": input_length - output_length,  # Approximation
        }

    def _count_entities(self, content: str) -> int:
        """
        Count HTML entities in content.

        Args:
            content: Content to analyze

        Returns:
            Number of HTML entities found
        """
        # Count standard entities
        entity_pattern = r"&[a-zA-Z]+;"
        named_entities = len(re.findall(entity_pattern, content))

        # Count numeric entities
        numeric_pattern = r"&#\d+;"
        decimal_entities = len(re.findall(numeric_pattern, content))

        hex_pattern = r"&#x[0-9A-Fa-f]+;"
        hex_entities = len(re.findall(hex_pattern, content))

        return named_entities + decimal_entities + hex_entities

    def _find_malformed_entities(self, content: str) -> List[str]:
        """
        Find malformed HTML entities in content.

        Args:
            content: Content to analyze

        Returns:
            List of malformed entities found
        """
        malformed = []

        # Check for entities without semicolons
        incomplete_pattern = r"&[a-zA-Z0-9]+(?![;])"
        incomplete = re.findall(incomplete_pattern, content)
        malformed.extend(incomplete)

        return malformed

    def _handle_remaining_entities(self, content: str) -> str:
        """
        Handle any remaining HTML entities that weren't decoded.

        Args:
            content: Content with potentially remaining entities

        Returns:
            Content with all entities decoded
        """
        # Handle specific cases that html.unescape might miss
        for entity, replacement in self.common_entities.items():
            content = content.replace(entity, replacement)

        return content

    def estimate_processing_time(
        self, content_length: int, options: ProcessingOptions
    ) -> float:
        """
        Estimate processing time for HTML entity decoding.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Entity decoding is very fast: 0.0002 seconds per character
        return content_length * 0.0002

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for HTML entity decoding.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Low memory usage: 2x content size
        return content_length * 2
