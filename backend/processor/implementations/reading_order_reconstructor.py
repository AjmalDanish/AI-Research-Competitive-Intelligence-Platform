"""
Reading Order Reconstructor Implementation.

Reconstructs reading order including:
- Logical content ordering
- Section hierarchy respect
- Reading flow optimization
"""

from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class ReadingOrderReconstructor(IContentProcessor):
    """
    Reconstructs reading order for content sections.

    This processor handles:
    - Logical content ordering
    - Section hierarchy respect
    - Reading flow optimization
    """

    def __init__(self):
        """Initialize reading order reconstructor."""
        self.stage = ProcessingStage.READING_ORDER_RECONSTRUCTION

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
        Reconstruct reading order for content.

        Args:
            content: Input content to reorder
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (reordered_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        # If we have heading associations, use them for ordering
        content_sections = metadata.get('content_sections', [])

        if content_sections and options.respect_html_structure:
            # Reorder content based on HTML structure
            reordered_content = self._reorder_by_html_structure(content_sections)
        elif options.fallback_to_visual_order:
            # Use visual order as fallback
            reordered_content = self._reorder_by_visual_order(content)
        else:
            # Keep original order
            reordered_content = content

        # Update metadata
        metadata["reading_order_reconstructed"] = True
        metadata["reading_order_segments"] = len(content_sections) if content_sections else 1

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["reading_order_segments"] = len(content_sections) if content_sections else 1

        return reordered_content, metadata

    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for reading order reconstruction.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if both options are enabled (conflict)
        if options.respect_html_structure and options.fallback_to_visual_order:
            errors.append("Both HTML structure and visual order fallback cannot be enabled")

        return errors

    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for reading order reconstruction.

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
            "reading_order_segments": input_length,  # Approximation
        }

    def _reorder_by_html_structure(self, content_sections: List[Dict[str, Any]]) -> str:
        """
        Reorder content based on HTML structure and heading hierarchy.

        Args:
            content_sections: List of content sections with heading info

        Returns:
            Content reordered by HTML structure
        """
        # Sort by position to maintain logical order
        sorted_sections = sorted(content_sections, key=lambda x: x['position'])

        # Concatenate content
        reordered = []
        for section in sorted_sections:
            if section.get('heading'):
                heading_text = f"{'#' * section['heading']['level']} {section['heading']['text']}"
                reordered.append(heading_text)

            reordered.append(section['content'])

        return '\n\n'.join(reordered)

    def _reorder_by_visual_order(self, content: str) -> str:
        """
        Reorder content based on visual order.

        Args:
            content: Content to reorder

        Returns:
            Content in visual order
        """
        # For visual order, we use simple line-based ordering
        lines = content.split('\n')

        # Remove empty lines and reorder
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for reading order reconstruction.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Reading order reconstruction is fast: 0.001 seconds per character
        return content_length * 0.001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for reading order reconstruction.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 3x content size
        return content_length * 3