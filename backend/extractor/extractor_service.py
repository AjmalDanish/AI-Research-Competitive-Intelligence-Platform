"""
Extraction Service.

Orchestrates the extraction pipeline using the registry.
ExtractionService should orchestrate only - business logic belongs in extractor implementations.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Optional

from backend.core.domain.extraction import (
    EntityType,
    ExtractionMetrics,
    ExtractionOptions,
    ExtractionResult,
    ExtractedEntity,
    ExtractorCapability,
    ExtractorContext,
)
from backend.core.interfaces.extractor import IExtractor
from backend.extractor.exceptions import (
    ExtractionError,
    ExtractionTimeoutError,
)
from backend.extractor.registry import ExtractionRegistry


class ExtractionService:
    """Main orchestration service for information extraction."""

    def __init__(
        self,
        registry: ExtractionRegistry,
        options: Optional[ExtractionOptions] = None,
        enable_timeout: bool = True,
    ):
        """
        Initialize extraction service.

        Args:
            registry: Extractor registry for managing extractors
            options: Extraction configuration options
            enable_timeout: Whether to enable timeout for extraction
        """
        self.registry = registry
        self.options = options or ExtractionOptions()
        self.enable_timeout = enable_timeout

        # Performance metrics
        self._total_extraction_count = 0
        self._successful_extraction_count = 0
        self._failed_extraction_count = 0

        # Validate registry dependencies
        self._validate_registry()

    def extract(
        self,
        processing_result: Any,
        source_url: str = "",
        options: Optional[ExtractionOptions] = None,
    ) -> ExtractionResult:
        """
        Extract entities from processing result.

        Args:
            processing_result: ProcessingResult from Milestone 5
            source_url: Optional source URL for tracking
            options: Optional extraction options (overrides service options)

        Returns:
            ExtractionResult with all extracted entities

        Raises:
            ExtractionError: If extraction fails
            ExtractionTimeoutError: If extraction times out
        """
        self._total_extraction_count += 1

        # Use provided options or service options
        extraction_options = options or self.options

        # Create extraction context
        context = ExtractorContext(
            processing_result=processing_result,
            configuration=extraction_options,
        )

        # Create extraction metrics
        extraction_metrics = ExtractionMetrics()
        extraction_metrics.input_content_length = len(context.get_content())

        # Create extraction result
        extraction_result = ExtractionResult(
            source_url=source_url,
            processing_started=datetime.now(),
        )

        # Store metrics in result
        extraction_result.metrics = extraction_metrics

        try:
            # Get enabled extractors in execution order
            enabled_extractors = self.registry.get_enabled_extractors(extraction_options)

            # Track start time
            pipeline_start_time = time.time()

            # Extract entities
            all_entities: list[ExtractedEntity] = []
            for extractor in enabled_extractors:
                extractor_name = extractor.get_name()

                # Check if extractor can extract from this context
                if not extractor.can_extract(context):
                    continue

                # Check if content should be skipped
                if extractor.should_skip_content(context):
                    continue

                # Validate context
                validation_errors = extractor.validate_context(context)
                if validation_errors and extraction_options.strict_validation:
                    extraction_metrics.validation_errors.extend(validation_errors)
                    continue

                # Execute extraction with timeout
                start_time = time.time()

                try:
                    entities = self._execute_extraction_with_timeout(extractor, context)

                    # Track metrics
                    duration = time.time() - start_time
                    extraction_metrics.add_extractor_timing(extractor_name, duration)

                    # Add entities to results
                    all_entities.extend(entities)

                    # Update entity counts
                    for entity in entities:
                        extraction_metrics.add_entity(entity.type)

                except ExtractionTimeoutError:
                    extraction_metrics.validation_errors.append(
                        f"{extractor_name} extraction timed out"
                    )
                    if extraction_options.strict_validation:
                        raise

                except ExtractionError as e:
                    extraction_metrics.validation_errors.append(
                        f"{extractor_name} extraction failed: {e}"
                    )
                    if extraction_options.strict_validation:
                        raise

            # Update total duration
            extraction_metrics.total_extraction_duration_seconds = time.time() - pipeline_start_time

            # Set entities in result
            extraction_result.entities = all_entities

            # Update validation status
            extraction_metrics.validation_passed = len(extraction_metrics.validation_errors) == 0

            # Calculate confidence distribution
            for entity in all_entities:
                extraction_metrics.add_confidence_score(entity.confidence)

            # Calculate quality score
            extraction_result.calculate_quality_score()

            # Update processing timestamps
            extraction_result.processing_completed = datetime.now()

            # Update success counter
            self._successful_extraction_count += 1

            return extraction_result

        except Exception as e:
            # Update failure counter
            self._failed_extraction_count += 1

            # Handle specific exceptions
            if isinstance(e, (ExtractionError, ExtractionTimeoutError)):
                raise

            # Wrap unexpected exceptions
            raise ExtractionError(f"Extraction failed: {e}") from e

    def extract_entities(
        self,
        processing_result: Any,
        entity_types: Optional[list[EntityType]] = None,
        source_url: str = "",
    ) -> ExtractionResult:
        """
        Extract specific entity types.

        Args:
            processing_result: ProcessingResult from Milestone 5
            entity_types: List of entity types to extract (None = all)
            source_url: Optional source URL for tracking

        Returns:
            ExtractionResult with filtered entities
        """
        extraction_result = self.extract(processing_result, source_url)

        if entity_types:
            # Filter entities by type
            extraction_result.entities = [
                entity for entity in extraction_result.entities if entity.type in entity_types
            ]

        return extraction_result

    def get_metrics(self) -> dict[str, Any]:
        """
        Get extraction service metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_extraction_count": self._total_extraction_count,
            "successful_extraction_count": self._successful_extraction_count,
            "failed_extraction_count": self._failed_extraction_count,
            "success_rate": (
                self._successful_extraction_count / self._total_extraction_count
                if self._total_extraction_count > 0
                else 0.0
            ),
            "registered_extractors": self.registry.get_extractor_statistics(),
        }

    def get_extractor_capabilities(self) -> dict[str, ExtractorCapability]:
        """
        Get capabilities of all registered extractors.

        Returns:
            Dictionary of extractor name to capability
        """
        return self.registry.get_extractor_capabilities()

    def is_extractor_available(self, extractor_name: str) -> bool:
        """
        Check if an extractor is available.

        Args:
            extractor_name: Name of the extractor

        Returns:
            True if available, False otherwise
        """
        return self.registry.get_extractor(extractor_name) is not None

    def update_options(self, options: ExtractionOptions) -> None:
        """
        Update extraction options.

        Args:
            options: New extraction options
        """
        self.options = options

    def _execute_extraction_with_timeout(
        self, extractor: IExtractor, context: ExtractorContext
    ) -> list[ExtractedEntity]:
        """
        Execute extraction with timeout protection.

        Args:
            extractor: Extractor to execute
            context: Extraction context

        Returns:
            List of extracted entities

        Raises:
            ExtractionTimeoutError: If extraction times out
        """
        if not self.enable_timeout:
            return extractor.extract(context)

        # For now, execute directly (timeout implementation requires async)
        # In production, this should use asyncio.wait_for or threading
        return extractor.extract(context)

    def _validate_registry(self) -> None:
        """
        Validate registry state.

        Raises:
            ExtractionError: If registry validation fails
        """
        # Check for dependency cycles
        if self.registry.has_dependency_cycle():
            raise ExtractionError("Registry has dependency cycles")

        # Check for dependency issues
        dependency_errors = self.registry.validate_dependencies()
        if dependency_errors:
            raise ExtractionError(
                f"Registry dependency validation failed: {', '.join(dependency_errors)}"
            )

        # Check if any extractors are registered
        if not self.registry.get_all_extractors():
            raise ExtractionError("No extractors registered in registry")
