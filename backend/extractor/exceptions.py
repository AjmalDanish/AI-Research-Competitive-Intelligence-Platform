"""
Extraction Exceptions.

Domain-specific exceptions for the extraction pipeline.
"""


class ExtractionError(Exception):
    """Base exception for extraction errors."""

    def __init__(self, message: str, extractor: Optional[str] = None):
        """
        Initialize extraction error.

        Args:
            message: Error message
            extractor: Name of the extractor that raised the error
        """
        self.extractor = extractor
        super().__init__(message)

    def __str__(self) -> str:
        if self.extractor:
            return f"[{self.extractor}] {super().__str__()}"
        return super().__str__()


class RuleLoadError(ExtractionError):
    """Raised when rules cannot be loaded."""

    def __init__(self, message: str, rule_file: Optional[str] = None):
        """
        Initialize rule load error.

        Args:
            message: Error message
            rule_file: Name of the rule file that failed to load
        """
        self.rule_file = rule_file
        super().__init__(message, extractor="rule_loader")

    def __str__(self) -> str:
        if self.rule_file:
            return f"Failed to load rules from '{self.rule_file}': {super().__str__()}"
        return super().__str__()


class RuleValidationError(ExtractionError):
    """Raised when rules fail validation."""

    def __init__(self, message: str, rule_name: Optional[str] = None):
        """
        Initialize rule validation error.

        Args:
            message: Error message
            rule_name: Name of the invalid rule
        """
        self.rule_name = rule_name
        super().__init__(message, extractor="rule_validator")

    def __str__(self) -> str:
        if self.rule_name:
            return f"Rule '{self.rule_name}' validation failed: {super().__str__()}"
        return super().__str__()


class RegistryError(ExtractionError):
    """Raised when registry operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize registry error.

        Args:
            message: Error message
            operation: Name of the failed registry operation
        """
        self.operation = operation
        super().__init__(message, extractor="registry")

    def __str__(self) -> str:
        if self.operation:
            return f"Registry operation '{self.operation}' failed: {super().__str__()}"
        return super().__str__()


class DependencyCycleError(RegistryError):
    """Raised when circular dependencies are detected."""

    def __init__(self, cycle: list[str]):
        """
        Initialize dependency cycle error.

        Args:
            cycle: List of extractor names forming the cycle
        """
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(
            f"Circular dependency detected: {cycle_str}", operation="dependency_validation"
        )

    def __str__(self) -> str:
        return super().__str__()


class ExtractorNotFoundError(RegistryError):
    """Raised when an extractor is not found."""

    def __init__(self, extractor_name: str):
        """
        Initialize extractor not found error.

        Args:
            extractor_name: Name of the extractor that was not found
        """
        self.extractor_name = extractor_name
        super().__init__(f"Extractor '{extractor_name}' not found", operation="get_extractor")

    def __str__(self) -> str:
        return super().__str__()


class ExtractorRegistrationError(RegistryError):
    """Raised when extractor registration fails."""

    def __init__(self, extractor_name: str, reason: str):
        """
        Initialize extractor registration error.

        Args:
            extractor_name: Name of the extractor that failed to register
            reason: Reason for registration failure
        """
        self.extractor_name = extractor_name
        super().__init__(
            f"Failed to register '{extractor_name}': {reason}", operation="register_extractor"
        )

    def __str__(self) -> str:
        return super().__str__()


class ExtractionTimeoutError(ExtractionError):
    """Raised when extraction operation times out."""

    def __init__(self, timeout_seconds: float, extractor: Optional[str] = None):
        """
        Initialize extraction timeout error.

        Args:
            timeout_seconds: Timeout duration in seconds
            extractor: Name of the extractor that timed out
        """
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Extraction timed out after {timeout_seconds} seconds", extractor=extractor
        )


class ExtractionValidationError(ExtractionError):
    """Raised when entity validation fails."""

    def __init__(self, message: str, entity_id: Optional[str] = None):
        """
        Initialize extraction validation error.

        Args:
            message: Error message
            entity_id: ID of the entity that failed validation
        """
        self.entity_id = entity_id
        super().__init__(message, extractor="validation_stage")

    def __str__(self) -> str:
        if self.entity_id:
            return f"Entity '{self.entity_id}' validation failed: {super().__str__()}"
        return super().__str__()


class NormalizationError(ExtractionError):
    """Raised when entity normalization fails."""

    def __init__(self, message: str, entity_id: Optional[str] = None):
        """
        Initialize normalization error.

        Args:
            message: Error message
            entity_id: ID of the entity that failed normalization
        """
        self.entity_id = entity_id
        super().__init__(message, extractor="normalization_stage")

    def __str__(self) -> str:
        if self.entity_id:
            return f"Entity '{self.entity_id}' normalization failed: {super().__str__()}"
        return super().__str__()


class DeduplicationError(ExtractionError):
    """Raised when deduplication fails."""

    def __init__(self, message: str, strategy: Optional[str] = None):
        """
        Initialize deduplication error.

        Args:
            message: Error message
            strategy: Name of the deduplication strategy that failed
        """
        self.strategy = strategy
        super().__init__(message, extractor="deduplication_stage")

    def __str__(self) -> str:
        if self.strategy:
            return f"Deduplication strategy '{self.strategy}' failed: {super().__str__()}"
        return super().__str__()


class ConfidenceAssignmentError(ExtractionError):
    """Raised when confidence assignment fails."""

    def __init__(self, message: str, entity_id: Optional[str] = None):
        """
        Initialize confidence assignment error.

        Args:
            message: Error message
            entity_id: ID of the entity that failed confidence assignment
        """
        self.entity_id = entity_id
        super().__init__(message, extractor="confidence_stage")

    def __str__(self) -> str:
        if self.entity_id:
            return f"Entity '{self.entity_id}' confidence assignment failed: {super().__str__()}"
        return super().__str__()
