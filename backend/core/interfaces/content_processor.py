"""
Content Processor Interface.

This module defines the abstract contract for all content processors.
Following the Open/Closed Principle, new processors can be added by implementing this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.core.domain.content_processor import (
    ProcessingResult,
    ProcessingOptions,
    ProcessingMetrics,
    ProcessingStage,
    TextSegment,
    ContentSection,
    NormalizedText,
    ContentMetadata,
)


class IContentProcessor(ABC):
    """
    Abstract contract for content processors.

    All content processors must implement this interface to ensure consistency
    and enable the Strategy Pattern for processor selection and composition.
    """

    @abstractmethod
    def get_stage(self) -> ProcessingStage:
        """
        Return the processing stage this processor handles.

        Returns:
            ProcessingStage enum value indicating which stage this processor implements
        """
        pass

    @abstractmethod
    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any],
    ) -> tuple[str, Dict[str, Any]]:
        """
        Process content according to the processor's specific logic.

        Args:
            content: Input content to process
            metadata: Content metadata that may be updated during processing
            options: Processing configuration options
            context: Processing context with intermediate results

        Returns:
            Tuple of (processed_content, updated_metadata)

        Raises:
            ProcessorError: If processing fails
        """
        pass

    @abstractmethod
    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content before processing.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        pass

    @abstractmethod
    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for this stage.

        Args:
            input_length: Length of input content
            output_length: Length of output content
            duration_seconds: Processing duration

        Returns:
            Dictionary of processing metrics
        """
        pass

    def is_enabled(self, options: ProcessingOptions) -> bool:
        """
        Check if this processor is enabled based on options.

        Args:
            options: Processing configuration options

        Returns:
            True if processor is enabled, False otherwise
        """
        # Default implementation checks if the stage is enabled
        stage = self.get_stage()

        if stage == ProcessingStage.WHITESPACE_NORMALIZATION:
            return options.enable_whitespace_normalization
        elif stage == ProcessingStage.UNICODE_NORMALIZATION:
            return options.enable_unicode_normalization
        elif stage == ProcessingStage.HTML_ENTITY_DECODING:
            return options.enable_html_entity_decoding
        elif stage == ProcessingStage.BOILERPLATE_REMOVAL:
            return options.enable_boilerplate_removal
        elif stage == ProcessingStage.NAVIGATION_FOOTER_REMOVAL:
            return options.enable_navigation_footer_removal
        elif stage == ProcessingStage.DUPLICATE_DETECTION:
            return options.enable_duplicate_detection
        elif stage == ProcessingStage.PARAGRAPH_RECONSTRUCTION:
            return options.enable_paragraph_reconstruction
        elif stage == ProcessingStage.HEADING_ASSOCIATION:
            return options.enable_heading_association
        elif stage == ProcessingStage.READING_ORDER_RECONSTRUCTION:
            return options.enable_reading_order_reconstruction
        elif stage == ProcessingStage.METADATA_CLEANUP:
            return options.enable_metadata_cleanup
        elif stage == ProcessingStage.VALIDATION:
            return options.enable_validation
        else:
            return True

    def get_stage_name(self) -> str:
        """
        Return the human-readable name of this processing stage.

        Returns:
            Human-readable stage name
        """
        return self.get_stage().value.replace("_", " ").title()

    def should_skip_content(self, content: str, options: ProcessingOptions) -> bool:
        """
        Determine if content should be skipped for this processor.

        Args:
            content: Content to check
            options: Processing configuration options

        Returns:
            True if processing should be skipped, False otherwise
        """
        # Skip empty content
        if not content or not content.strip():
            return True

        # Skip if content exceeds max length
        if len(content) > options.max_content_length:
            return True

        return False

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for this stage.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Default estimation: 0.001 seconds per character
        return content_length * 0.001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for this stage.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Default estimation: 3x content size
        return content_length * 3
