"""
Processing Service - Content Processing Orchestration.

This service orchestrates the content processing pipeline, managing the sequence
of processing stages and ensuring clean architecture principles are maintained.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.domain.content_processor import (
    ProcessingResult,
    ProcessingMetrics,
    ProcessingOptions,
    ProcessingStage,
    ProcessingStageResult,
    ContentSection,
    TextSegment,
    NormalizedText,
    ContentMetadata,
)
from backend.core.interfaces.content_processor import IContentProcessor
from backend.processor.exceptions import (
    ProcessorError,
    ProcessorNotAvailableError,
    ProcessingTimeoutError,
    ProcessingValidationError,
)
from backend.processor.implementations import (
    WhitespaceNormalizer,
    UnicodeNormalizer,
    HTMLEntityDecoder,
    BoilerplateRemover,
    NavigationRemover,
    DuplicateDetector,
    ParagraphReconstructor,
    HeadingAssociator,
    ReadingOrderReconstructor,
    MetadataCleaner,
    ContentValidator,
)


class ProcessingService:
    """
    Orchestrates the content processing pipeline.

    This service manages the sequence of processing stages and ensures:
    - Proper pipeline execution order
    - Error handling and recovery
    - Performance metrics collection
    - Context management between stages

    Responsibilities (orchestration only):
    - Pipeline execution coordination
    - Processor registration and selection
    - Error handling and recovery
    - Metrics collection and reporting

    Anti-patterns to avoid:
    - Business logic (content extraction, analysis)
    - Domain-specific processing rules
    - AI/LLM integration (belongs in future milestones)
    - Persistence concerns (belongs in future milestones)
    """

    def __init__(
        self,
        options: Optional[ProcessingOptions] = None,
        processors: Optional[List[IContentProcessor]] = None,
        enable_timeout: bool = True,
    ):
        """
        Initialize processing service.

        Args:
            options: Processing configuration options
            processors: List of processors to use (uses default if None)
            enable_timeout: Whether to enable timeout protection
        """
        self.options = options or ProcessingOptions()
        self.enable_timeout = enable_timeout

        # Register default processors in pipeline order
        self._processors: Dict[ProcessingStage, IContentProcessor] = {}

        if processors is None:
            self._register_default_processors()
        else:
            self._register_processors(processors)

        # Performance metrics
        self._total_processing_count = 0
        self._successful_processing_count = 0
        self._failed_processing_count = 0

    def _register_default_processors(self) -> None:
        """Register the default processing pipeline."""
        # Register processors in pipeline order
        self._processors[ProcessingStage.WHITESPACE_NORMALIZATION] = (
            WhitespaceNormalizer()
        )
        self._processors[ProcessingStage.UNICODE_NORMALIZATION] = UnicodeNormalizer()
        self._processors[ProcessingStage.HTML_ENTITY_DECODING] = HTMLEntityDecoder()
        self._processors[ProcessingStage.BOILERPLATE_REMOVAL] = BoilerplateRemover()
        self._processors[ProcessingStage.NAVIGATION_FOOTER_REMOVAL] = (
            NavigationRemover()
        )
        self._processors[ProcessingStage.DUPLICATE_DETECTION] = DuplicateDetector()
        self._processors[ProcessingStage.PARAGRAPH_RECONSTRUCTION] = (
            ParagraphReconstructor()
        )
        self._processors[ProcessingStage.HEADING_ASSOCIATION] = HeadingAssociator()
        self._processors[ProcessingStage.READING_ORDER_RECONSTRUCTION] = (
            ReadingOrderReconstructor()
        )
        self._processors[ProcessingStage.METADATA_CLEANUP] = MetadataCleaner()
        self._processors[ProcessingStage.VALIDATION] = ContentValidator()

    def _register_processors(self, processors: List[IContentProcessor]) -> None:
        """
        Register custom processors.

        Args:
            processors: List of processors to register
        """
        for processor in processors:
            self._processors[processor.get_stage()] = processor

    def register_processor(self, processor: IContentProcessor) -> None:
        """
        Register a single processor.

        Args:
            processor: Processor to register
        """
        self._processors[processor.get_stage()] = processor

    def unregister_processor(self, stage: ProcessingStage) -> None:
        """
        Unregister a processor by stage.

        Args:
            stage: Processing stage to unregister
        """
        if stage in self._processors:
            del self._processors[stage]

    def get_processor(self, stage: ProcessingStage) -> IContentProcessor:
        """
        Get a processor by stage.

        Args:
            stage: Processing stage

        Returns:
            Processor instance

        Raises:
            ProcessorNotAvailableError: If processor not available
        """
        if stage not in self._processors:
            raise ProcessorNotAvailableError(
                f"Processor for stage '{stage.value}' not available"
            )

        return self._processors[stage]

    def process(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
    ) -> ProcessingResult:
        """
        Process content through the complete pipeline.

        Args:
            content: Input content to process
            metadata: Optional content metadata
            source_url: Optional source URL for tracking

        Returns:
            ProcessingResult with all processed content and metrics

        Raises:
            ProcessorError: If processing fails
            ProcessingTimeoutError: If processing times out
            ProcessingValidationError: If validation fails
        """
        self._total_processing_count += 1

        # Initialize metadata
        if metadata is None:
            metadata = {}

        # Set source URL
        source_url = source_url or ""

        # Initialize processing context
        context = {
            "timestamp": datetime.now(),
            "metrics": {},
        }

        # Create processing metrics
        processing_metrics = ProcessingMetrics()
        processing_metrics.input_content_length = len(content)

        # Track original content
        original_content = content

        try:
            # Process through pipeline stages
            for stage in ProcessingStage:
                if stage not in self._processors:
                    continue

                processor = self._processors[stage]

                # Check if processor is enabled
                if not processor.is_enabled(self.options):
                    continue

                # Check if content should be skipped
                if processor.should_skip_content(content, self.options):
                    continue

                # Process this stage
                start_time = time.time()

                # Validate before processing
                validation_errors = processor.validate(content, metadata, self.options)
                if validation_errors and self.options.strict_validation:
                    processing_metrics.validation_errors.extend(validation_errors)

                # Execute processing
                content, metadata = processor.process(
                    content, metadata, self.options, context
                )

                end_time = time.time()
                duration = end_time - start_time

                # Create stage result
                stage_result = ProcessingStageResult(
                    stage=stage,
                    success=True,
                    duration_seconds=duration,
                    errors=[],
                    warnings=[],
                    metrics=processor.get_processing_metrics(
                        len(original_content), len(content), duration
                    ),
                )

                processing_metrics.add_stage_result(stage_result)

                # Check for timeout
                if self.enable_timeout and duration > self.options.timeout_seconds:
                    raise ProcessingTimeoutError(
                        self.options.timeout_seconds, stage.value
                    )

            # Create normalized text
            normalized_text = NormalizedText(
                original_text=original_content, normalized_text=content
            )
            normalized_text.calculate_statistics()

            # Create text segments (simplified implementation)
            text_segments = self._create_text_segments(content, context)

            # Create content sections
            content_sections = self._create_content_sections(text_segments, metadata)

            # Create content metadata
            content_metadata = self._create_content_metadata(metadata)

            # Calculate final metrics
            processing_metrics.output_content_length = len(content)
            processing_metrics.content_compression_ratio = (
                len(content) / len(original_content) if len(original_content) > 0 else 0
            )
            processing_metrics.validation_passed = (
                len(processing_metrics.validation_errors) == 0
            )

            # Update validation status in metadata
            content_metadata.validation_passed = processing_metrics.validation_passed

            # Create processing result
            result = ProcessingResult(
                source_url=source_url,
                original_content=original_content,
                normalized_text=normalized_text,
                content_sections=content_sections,
                text_segments=text_segments,
                metadata=content_metadata,
                metrics=processing_metrics,
                processing_complete=True,
                processing_started=context["timestamp"],  # type: ignore[arg-type]
                processing_completed=datetime.now(),
            )

            # Calculate quality score
            result.calculate_quality_score()

            # Update success counter
            self._successful_processing_count += 1

            return result

        except Exception as e:
            # Update failure counter
            self._failed_processing_count += 1

            # Handle specific exceptions
            if isinstance(
                e, (ProcessorError, ProcessingTimeoutError, ProcessingValidationError)
            ):
                raise

            # Wrap unexpected exceptions
            raise ProcessorError(f"Processing failed: {str(e)}") from e

    def _create_text_segments(
        self, content: str, context: Dict[str, Any]
    ) -> List[TextSegment]:
        """
        Create text segments from processed content.

        Args:
            content: Processed content
            context: Processing context

        Returns:
            List of text segments
        """
        segments = []
        lines = content.split("\n")

        for position, line in enumerate(lines):
            if line.strip():
                # Determine segment type (simplified)
                segment_type = "paragraph"
                if line.strip().startswith("#"):
                    segment_type = "heading"

                segment = TextSegment(
                    text=line.strip(),
                    segment_type=segment_type,
                    position=position,
                    start_index=position,
                    end_index=position + len(line),
                    level=1 if line.strip().startswith("#") else None,
                )

                # Calculate basic metrics
                segment.word_count = len(segment.text.split())
                segment.character_count = len(segment.text)
                if segment.word_count > 0:
                    segment.average_word_length = (
                        segment.character_count / segment.word_count
                    )

                segments.append(segment)

        return segments

    def _create_content_sections(
        self, segments: List[TextSegment], metadata: Dict[str, Any]
    ) -> List[ContentSection]:
        """
        Create content sections from text segments.

        Args:
            segments: Text segments
            metadata: Content metadata

        Returns:
            List of content sections
        """
        # Simple implementation - one section for all content
        sections = [
            ContentSection(
                section_id="main",
                heading=None,
                segments=segments,
                position=0,
                section_type="content",
            )
        ]

        # Calculate section metrics
        for section in sections:
            section.calculate_metrics()

        return sections

    def _create_content_metadata(self, metadata: Dict[str, Any]) -> ContentMetadata:
        """
        Create content metadata from processed metadata.

        Args:
            metadata: Processed metadata

        Returns:
            ContentMetadata object
        """
        return ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description"),
            keywords=metadata.get("keywords", []),
            author=metadata.get("author"),
            publish_date=metadata.get("publish_date"),
            language=metadata.get("language"),
            content_type=metadata.get("content_type"),
            canonical_url=metadata.get("canonical_url"),
            og_title=metadata.get("og_title"),
            og_description=metadata.get("og_description"),
            og_image=metadata.get("og_image"),
            og_type=metadata.get("og_type"),
            twitter_title=metadata.get("twitter_title"),
            twitter_description=metadata.get("twitter_description"),
            twitter_image=metadata.get("twitter_image"),
            twitter_card_type=metadata.get("twitter_card_type"),
            metadata_normalized=metadata.get("metadata_normalized", False),
            duplicates_removed=metadata.get("duplicates_removed", False),
            validation_passed=metadata.get("validation_passed", True),
        )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the service.

        Returns:
            Dictionary of performance metrics
        """
        return {
            "total_processing_count": self._total_processing_count,
            "successful_processing_count": self._successful_processing_count,
            "failed_processing_count": self._failed_processing_count,
            "success_rate": (
                self._successful_processing_count / self._total_processing_count
                if self._total_processing_count > 0
                else 0
            ),
            "registered_processors": list(self._processors.keys()),
        }

    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self._total_processing_count = 0
        self._successful_processing_count = 0
        self._failed_processing_count = 0

    def get_available_stages(self) -> List[ProcessingStage]:
        """
        Get list of available processing stages.

        Returns:
            List of ProcessingStage enum values
        """
        return list(self._processors.keys())

    def is_stage_available(self, stage: ProcessingStage) -> bool:
        """
        Check if a processing stage is available.

        Args:
            stage: Processing stage to check

        Returns:
            True if stage is available
        """
        return stage in self._processors

    def enable_stage(self, stage: ProcessingStage, enabled: bool = True) -> None:
        """
        Enable or disable a processing stage.

        Args:
            stage: Processing stage to enable/disable
            enabled: Whether to enable the stage
        """
        if stage == ProcessingStage.WHITESPACE_NORMALIZATION:
            self.options.enable_whitespace_normalization = enabled
        elif stage == ProcessingStage.UNICODE_NORMALIZATION:
            self.options.enable_unicode_normalization = enabled
        elif stage == ProcessingStage.HTML_ENTITY_DECODING:
            self.options.enable_html_entity_decoding = enabled
        elif stage == ProcessingStage.BOILERPLATE_REMOVAL:
            self.options.enable_boilerplate_removal = enabled
        elif stage == ProcessingStage.NAVIGATION_FOOTER_REMOVAL:
            self.options.enable_navigation_footer_removal = enabled
        elif stage == ProcessingStage.DUPLICATE_DETECTION:
            self.options.enable_duplicate_detection = enabled
        elif stage == ProcessingStage.PARAGRAPH_RECONSTRUCTION:
            self.options.enable_paragraph_reconstruction = enabled
        elif stage == ProcessingStage.HEADING_ASSOCIATION:
            self.options.enable_heading_association = enabled
        elif stage == ProcessingStage.READING_ORDER_RECONSTRUCTION:
            self.options.enable_reading_order_reconstruction = enabled
        elif stage == ProcessingStage.METADATA_CLEANUP:
            self.options.enable_metadata_cleanup = enabled
        elif stage == ProcessingStage.VALIDATION:
            self.options.enable_validation = enabled
