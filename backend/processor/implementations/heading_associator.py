"""
Heading Associator Implementation.

Associates content sections with appropriate headings including:
- Heading hierarchy detection
- Content-to-heading mapping
- Section boundary identification
"""

import re
from typing import Any, Dict, List, Optional

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class HeadingAssociator(IContentProcessor):
    """
    Associates content sections with appropriate headings.

    This processor handles:
    - Heading hierarchy detection
    - Content-to-heading mapping
    - Section boundary identification
    - Parent-child relationship establishment
    """

    def __init__(self):
        """Initialize heading associator."""
        self.stage = ProcessingStage.HEADING_ASSOCIATION

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
        Associate content sections with headings.

        Args:
            content: Input content with headings
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (annotated_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        # Extract headings with hierarchy
        headings = self._extract_headings(content)

        # Associate content with headings
        content_sections = self._associate_content_with_headings(content, headings, options)

        # Update metadata
        metadata["headings_associated"] = True
        metadata["heading_count"] = len(headings)
        metadata["content_sections"] = content_sections
        metadata["content_section_count"] = len(content_sections)

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["headings_associated"] = len(headings)

        return content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for heading association.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate max heading distance
        if options.max_heading_distance < 1:
            errors.append("Maximum heading distance must be positive")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for heading association.

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
            "headings_found": input_length,  # Approximation
        }

    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract headings with their levels and positions.

        Args:
            content: Content to extract headings from

        Returns:
            List of heading dictionaries
        """
        headings = []

        # Find all markdown-style headings
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        for line_num, line in enumerate(content.split("\n"), 1):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()

                headings.append(
                    {
                        "level": level,
                        "text": text,
                        "line_number": line_num,
                        "position": len(headings),
                    }
                )

        return headings

    def _associate_content_with_headings(
        self, content: str, headings: List[Dict[str, Any]], options: ProcessingOptions
    ) -> List[Dict[str, Any]]:
        """
        Associate content sections with appropriate headings.

        Args:
            content: Content to associate
            headings: List of headings
            options: Processing configuration options

        Returns:
            List of content sections with heading associations
        """
        if not headings:
            # No headings, create single section
            return [{"heading": None, "content": content, "heading_level": 0, "position": 0}]

        content_lines = content.split("\n")
        sections = []
        current_heading = None
        current_section_content = []

        # Initialize with first heading
        if headings:
            current_heading = headings[0]

        for line_num, line in enumerate(content_lines, 1):
            # Check if this line is a heading
            is_heading = False
            for heading in headings:
                if heading["line_number"] == line_num:
                    # Save current section if we have content
                    if current_section_content:
                        sections.append(
                            {
                                "heading": current_heading,
                                "content": "\n".join(current_section_content),
                                "heading_level": current_heading["level"] if current_heading else 0,
                                "position": len(sections),
                            }
                        )

                    # Start new section
                    current_heading = heading
                    current_section_content = []
                    is_heading = True
                    break

            if not is_heading:
                current_section_content.append(line)

        # Don't forget the last section
        if current_section_content:
            sections.append(
                {
                    "heading": current_heading,
                    "content": "\n".join(current_section_content),
                    "heading_level": current_heading["level"] if current_heading else 0,
                    "position": len(sections),
                }
            )

        return sections

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for heading association.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Heading association is moderately fast: 0.002 seconds per character
        return content_length * 0.002

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for heading association.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 3x content size
        return content_length * 3
