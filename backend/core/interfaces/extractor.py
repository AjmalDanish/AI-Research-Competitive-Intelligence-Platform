"""
Extraction Interfaces.

This module defines the core interfaces for the extraction pipeline.
All extractors must implement these interfaces to maintain Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any

from backend.core.domain.extraction import (
    ExtractedEntity,
    ExtractionOptions,
    ExtractorCapability,
    ExtractorContext,
)


class IExtractor(ABC):
    """Interface for all entity extractors."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the extractor."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get the version of the extractor."""
        pass

    @abstractmethod
    def get_capability(self) -> ExtractorCapability:
        """Get the capability descriptor for this extractor."""
        pass

    @abstractmethod
    def can_extract(self, context: ExtractorContext) -> bool:
        """Check if this extractor can extract from the given context."""
        pass

    @abstractmethod
    def extract(self, context: ExtractorContext) -> list[ExtractedEntity]:
        """
        Extract entities from the given context.

        Args:
            context: Extraction context containing content and metadata

        Returns:
            List of extracted entities

        Raises:
            ExtractionError: If extraction fails
        """
        pass

    @abstractmethod
    def is_enabled(self, options: ExtractionOptions) -> bool:
        """Check if this extractor is enabled."""
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Get list of extractor names this extractor depends on."""
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get extraction priority (higher = earlier execution)."""
        pass

    def should_skip_content(self, context: ExtractorContext) -> bool:
        """
        Check if content should be skipped.

        Args:
            context: Extraction context

        Returns:
            True if content should be skipped, False otherwise
        """
        content = context.get_content()
        return not content or len(content.strip()) < 10

    def validate_context(self, context: ExtractorContext) -> list[str]:
        """
        Validate extraction context.

        Args:
            context: Extraction context to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not context.processing_result:
            errors.append("Processing result is required")

        if not context.configuration:
            errors.append("Configuration is required")

        content = context.get_content()
        if not content:
            errors.append("Content is empty")

        return errors


class IExtractionStage(ABC):
    """Interface for extraction pipeline stages."""

    @abstractmethod
    def get_stage_name(self) -> str:
        """Get the name of this stage."""
        pass

    @abstractmethod
    def execute(
        self, entities: list[ExtractedEntity], context: ExtractorContext
    ) -> list[ExtractedEntity]:
        """
        Execute this stage on the entities.

        Args:
            entities: List of entities to process
            context: Extraction context

        Returns:
            List of processed entities

        Raises:
            ExtractionError: If stage execution fails
        """
        pass

    @abstractmethod
    def is_enabled(self, options: ExtractionOptions) -> bool:
        """Check if this stage is enabled."""
        pass

    @abstractmethod
    def get_execution_order(self) -> int:
        """Get execution order (lower = earlier execution)."""
        pass


class IExtractorCapability(ABC):
    """Interface for extractor capability descriptors."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the extractor."""
        pass

    @abstractmethod
    def get_supported_entity_types(self) -> list[str]:
        """Get the list of entity types this extractor supports."""
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Get the list of extractor dependencies."""
        pass

    @abstractmethod
    def is_deterministic(self) -> bool:
        """Check if the extractor is deterministic."""
        pass

    @abstractmethod
    def get_confidence_strategy(self) -> str:
        """Get the confidence scoring strategy."""
        pass


class IRuleProvider(ABC):
    """Interface for rule providers."""

    @abstractmethod
    def get_rules(self, extractor_name: str) -> dict[str, Any]:
        """
        Get rules for a specific extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Dictionary of rules

        Raises:
            RuleLoadError: If rules cannot be loaded
        """
        pass

    @abstractmethod
    def get_rule(self, extractor_name: str, rule_name: str) -> dict[str, Any]:
        """
        Get a specific rule.

        Args:
            extractor_name: Name of the extractor
            rule_name: Name of the rule

        Returns:
            Rule configuration

        Raises:
            RuleNotFoundError: If rule is not found
        """
        pass

    @abstractmethod
    def validate_rules(self, extractor_name: str) -> bool:
        """
        Validate rules for an extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            True if rules are valid, False otherwise
        """
        pass

    @abstractmethod
    def get_rule_version(self, extractor_name: str) -> str:
        """
        Get the version of rules for an extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Version string
        """
        pass


class IExtractionRegistry(ABC):
    """Interface for extractor registry."""

    @abstractmethod
    def register_extractor(self, extractor: IExtractor) -> None:
        """
        Register an extractor.

        Args:
            extractor: Extractor instance to register

        Raises:
            RegistryError: If registration fails
        """
        pass

    @abstractmethod
    def unregister_extractor(self, extractor_name: str) -> None:
        """
        Unregister an extractor.

        Args:
            extractor_name: Name of the extractor to unregister
        """
        pass

    @abstractmethod
    def get_extractor(self, extractor_name: str) -> IExtractor | None:
        """
        Get an extractor by name.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Extractor instance or None if not found
        """
        pass

    @abstractmethod
    def get_all_extractors(self) -> dict[str, IExtractor]:
        """
        Get all registered extractors.

        Returns:
            Dictionary of extractor name to extractor instance
        """
        pass

    @abstractmethod
    def get_enabled_extractors(self, options: ExtractionOptions) -> list[IExtractor]:
        """
        Get all enabled extractors.

        Args:
            options: Extraction options

        Returns:
            List of enabled extractors in execution order
        """
        pass

    @abstractmethod
    def get_extractor_capabilities(self) -> dict[str, ExtractorCapability]:
        """
        Get capabilities of all registered extractors.

        Returns:
            Dictionary of extractor name to capability
        """
        pass

    @abstractmethod
    def validate_dependencies(self) -> list[str]:
        """
        Validate all extractor dependencies.

        Returns:
            List of validation errors (empty if valid)
        """
        pass

    @abstractmethod
    def get_execution_order(self) -> list[str]:
        """
        Get the execution order based on dependencies.

        Returns:
            List of extractor names in execution order

        Raises:
            DependencyCycleError: If circular dependencies are detected
        """
        pass


class IRuleLoader(ABC):
    """Interface for rule loaders."""

    @abstractmethod
    def load_rules(self, extractor_name: str) -> dict[str, Any]:
        """
        Load rules for an extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Dictionary of rules

        Raises:
            RuleLoadError: If rules cannot be loaded
        """
        pass

    @abstractmethod
    def validate_rules(self, rules: dict[str, Any]) -> bool:
        """
        Validate rule structure.

        Args:
            rules: Rules to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def get_rule_schema(self) -> dict[str, Any]:
        """
        Get the expected rule schema.

        Returns:
            Schema definition
        """
        pass

    @abstractmethod
    def get_rules_directory(self) -> str:
        """
        Get the directory containing rule files.

        Returns:
            Path to rules directory
        """
        pass


class INormalizationStage(IExtractionStage):
    """Interface for normalization stage."""

    @abstractmethod
    def normalize_entity(
        self, entity: ExtractedEntity, context: ExtractorContext
    ) -> ExtractedEntity:
        """
        Normalize a single entity.

        Args:
            entity: Entity to normalize
            context: Extraction context

        Returns:
            Normalized entity
        """
        pass


class IValidationStage(IExtractionStage):
    """Interface for validation stage."""

    @abstractmethod
    def validate_entity(
        self, entity: ExtractedEntity, context: ExtractorContext
    ) -> tuple[bool, list[str]]:
        """
        Validate a single entity.

        Args:
            entity: Entity to validate
            context: Extraction context

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass


class IDeduplicationStage(IExtractionStage):
    """Interface for deduplication stage."""

    @abstractmethod
    def find_duplicates(
        self, entities: list[ExtractedEntity], context: ExtractorContext
    ) -> dict[str, list[int]]:
        """
        Find duplicate entities.

        Args:
            entities: List of entities to check
            context: Extraction context

        Returns:
            Dictionary mapping normalized value to list of indices
        """
        pass

    @abstractmethod
    def resolve_duplicates(
        self,
        duplicates: dict[str, list[int]],
        entities: list[ExtractedEntity],
        context: ExtractorContext,
    ) -> list[ExtractedEntity]:
        """
        Resolve duplicates by keeping the best match.

        Args:
            duplicates: Dictionary of duplicates
            entities: List of all entities
            context: Extraction context

        Returns:
            List of entities with duplicates removed
        """
        pass


class IConfidenceAssignmentStage(IExtractionStage):
    """Interface for confidence assignment stage."""

    @abstractmethod
    def assign_confidence(self, entity: ExtractedEntity, context: ExtractorContext) -> float:
        """
        Assign confidence score to an entity.

        Args:
            entity: Entity to score
            context: Extraction context

        Returns:
            Confidence score (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def generate_confidence_reason(
        self, entity: ExtractedEntity, confidence: float, context: ExtractorContext
    ) -> str:
        """
        Generate explanation for confidence score.

        Args:
            entity: Entity being scored
            confidence: Assigned confidence score
            context: Extraction context

        Returns:
            Human-readable explanation
        """
        pass
