# Content Processor Extension Guide

## Overview

This guide explains how to add new content processor implementations to the AI Website Intelligence Platform without modifying existing code, following the **Open/Closed Principle** from SOLID design principles.

## Open/Closed Principle

**"Software entities should be open for extension, but closed for modification."**

In the context of the Content Processor Foundation:
- ✅ **Open for extension**: New processors can be added by implementing the `IContentProcessor` interface
- ❌ **Closed for modification**: Existing processors are never modified
- ✅ **Pipeline extensibility**: New stages can be added to the processing pipeline
- ✅ **Configuration flexibility**: New processors can be controlled via options

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     IContentProcessor Interface                         │
│                 (Abstract Base Class)                                 │
│                                                                   │
│  + get_stage() → ProcessingStage                                      │
│  + process(content, metadata, options, context) → tuple[str, Dict]   │
│  + validate(content, metadata, options) → List[str]                       │
│  + get_processing_metrics(input_len, output_len, duration) → Dict       │
│  + is_enabled(options) → bool                                         │
│  + should_skip_content(content, options) → bool                         │
│  + estimate_processing_time(content_length, options) → float            │
│  + get_memory_usage_estimate(content_length) → int                         │
│                                                                   │
┌─────────────────────────────────────────────────────────────────┤
│               Open/Closed Principle                                  │
│               (Extensible without modifying)                         │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │ implements
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        │                 │                 │
┌───────┴──────┐  ┌──────┴───────┐  ┌──────┴────────┐
│Whitespace │  │Unicode Normalizer│  │ Custom     │
│Normalizer │  │                 │  │ Processor  │
└──────────────┘  └─────────────────┘  └─────────────┘

No existing code needs modification when adding CustomProcessor!
```

## Step-by-Step Guide

### Step 1: Create Processor Implementation File

**Location:** `backend/processor/implementations/your_processor.py`

**Template:**
```python
"""
Custom Content Processor Implementation.

This processor demonstrates how to create a new processor implementation
following the IContentProcessor interface without modifying existing code.
"""

from typing import Any, Dict, List
from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions
from backend.processor.exceptions import ProcessorError


class CustomProcessor(IContentProcessor):
    """
    Custom processor for specific content processing needs.

    This class demonstrates the Open/Closed Principle:
    - Implements IContentProcessor interface
    - No modification to existing processors needed
    - Can be used immediately with ProcessingService
    - Deterministic processing (no randomness)
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the custom processor.

        Args:
            config: Optional configuration dictionary for processor behavior
        """
        self.config = config or {}
        # Initialize your processor-specific resources here
        self.processing_enabled = self.config.get("processing_enabled", True)
        self.processing_name = self.config.get("processor_name", "CustomProcessor")

    def get_stage(self) -> ProcessingStage:
        """
        Return the processing stage this processor handles.

        Returns:
            ProcessingStage enum value indicating which stage this processor implements
        """
        # For this example, we'll add it as a custom stage
        # In production, you'd use an existing stage or request adding a new one to ProcessingStage enum
        return ProcessingStage.DUPLICATE_DETECTION  # Reuse existing stage for this example

    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any]
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
        try:
            import time  # For metrics tracking
            start_time = time.time()

            # Skip processing if not enabled
            if not self.is_enabled(options):
                return content, metadata

            # Skip if content should be skipped
            if self.should_skip_content(content, options):
                return content, metadata

            # Pre-validation
            validation_errors = self.validate(content, metadata, options)
            if validation_errors and options.strict_validation:
                from backend.processor.exceptions import ProcessingValidationError
                raise ProcessingValidationError(validation_errors, self.get_stage_name())

            # Implement your custom processing logic here
            processed_content = self._custom_processing_logic(content, metadata, options)

            end_time = time.time()
            duration = end_time - start_time

            # Update metadata with processing status
            metadata["custom_processed"] = True
            metadata["custom_processing_timestamp"] = time.time()

            # Track metrics
            context.setdefault("metrics", {})
            context["metrics"]["custom_processor_count"] = context["metrics"].get("custom_processor_count", 0) + 1

            return processed_content, metadata

        except Exception as e:
            raise ProcessorError(f"Custom processor failed: {str(e)}") from e

    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> List[str]:
        """
        Validate content before processing.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Example validation: Check content length
        if not content or not content.strip():
            errors.append("Content cannot be empty")

        # Add your custom validation logic here
        # Example: Check for specific patterns
        import re
        if "forbidden_pattern" in content.lower():
            errors.append("Content contains forbidden pattern")

        # Check configuration requirements
        if self.config.get("require_specific_pattern", False):
            if "required_pattern" not in content.lower():
                errors.append("Content missing required pattern")

        return errors

    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
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
        reduction = input_length - output_length
        reduction_percentage = (reduction / input_length * 100) if input_length > 0 else 0

        return {
            "input_length": input_length,
            "output_length": output_length,
            "reduction": reduction,
            "reduction_percentage": reduction_percentage,
            "duration_seconds": duration_seconds,
            "processor_name": self.processing_name,
        }

    def _custom_processing_logic(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> str:
        """
        Implement your custom processing logic here.

        Args:
            content: Content to process
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            Processed content
        """
        # Example: Remove specific patterns
        import re
        processed_content = content

        # Remove specific unwanted patterns
        if self.config.get("remove_ads", False):
            ad_pattern = r'Advertisement.*?(?=\n\n|$)'
            processed_content = re.sub(ad_pattern, '', processed_content, flags=re.IGNORECASE | re.DOTALL)

        # Remove social media mentions
        if self.config.get("remove_social", False):
            social_pattern = r'(Follow us on|Connect with us|Share on)'
            processed_content = re.sub(social_pattern, '', processed_content, flags=re.IGNORECASE | re.DOTALL)

        # Custom transformation logic
        if self.config.get("transform_text", False):
            processed_content = self._transform_text(processed_content, metadata)

        return processed_content

    def _transform_text(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Apply custom text transformation.

        Args:
            content: Content to transform
            metadata: Content metadata

        Returns:
            Transformed content
        """
        # Example: Apply custom text transformations
        transformed = content

        # Example: Convert to title case for titles
        if self.config.get("title_case_conversion", False):
            lines = transformed.split('\n')
            transformed = '\n'.join(line.capitalize() for line in lines)

        return transformed

    def is_enabled(self, options: ProcessingOptions) -> ProcessingOptions:
        """
        Check if this processor is enabled based on options.

        Args:
            options: Processing configuration options

        Returns:
            True if processor is enabled, False otherwise
        """
        return self.processing_enabled

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

        # Skip if content is too short
        if len(content) < self.config.get("min_content_length", options.min_paragraph_length):
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
        # Base estimation: 0.001 seconds per character
        base_time = content_length * 0.001

        # Apply configuration-based multiplier if needed
        multiplier = self.config.get("processing_multiplier", 1.0)
        return base_time * multiplier

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for this stage.

        Args:
            content_length: Content length to process

        Returns:
            Estimated memory usage in bytes
        """
        # Base estimation: 2x content size
        base_memory = content_length * 2

        # Apply configuration-based multiplier if needed
        multiplier = self.config.get("memory_multiplier", 1.0)
        return int(base_memory * multiplier)

    def get_stage_name(self) -> str:
        """
        Return the human-readable name of this processing stage.

        Returns:
            Human-readable stage name
        """
        return "Custom Processor"
```

### Step 2: Update Module Exports

**File:** `backend/processor/implementations/__init__.py`

**Add your processor to exports:**
```python
"""
Content Processor implementations module.

This module exports all available processor implementations.
Following Open/Closed Principle: new processors can be added
without modifying existing code.
"""

from backend.processor.implementations.whitespace_normalizer import WhitespaceNormalizer
from backend.processor.implementations.unicode_normalizer import UnicodeNormalizer
from backend.processor.implementations.html_entity_decoder import HTMLEntityDecoder
from backend.processor.implementations.boilerplate_remover import BoilerplateRemover
from backend.processor.implementations.navigation_remover import NavigationRemover
from backend.processor.implementations.duplicate_detector import DuplicateDetector
from backend.processor.implementations.paragraph_reconstructor import ParagraphReconstructor
from backend.processor.implementations.heading_associator import HeadingAssociator
from backend.processor.implementations.reading_order_reconstructor import ReadingOrderReconstructor
from backend.processor.implementations.metadata_cleaner import MetadataCleaner
from backend.processor.implementations.content_validator import ContentValidator
from backend.processor.implementations.your_processor import CustomProcessor  # Add this line

__all__ = [
    "WhitespaceNormalizer",
    "UnicodeNormalizer",
    "HTMLEntityDecoder",
    "BoilerplateRemover",
    "NavigationRemover",
    "DuplicateDetector",
    "ParagraphReconstructor",
    "HeadingAssociator",
    "ReadingOrderReconstructor",
    "MetadataCleaner",
    "ContentValidator",
    "CustomProcessor",  # Add this line
]
```

### Step 3: Use Your Custom Processor

**Instantiating the Processor:**
```python
from backend.processor import ProcessingService, CustomProcessor, ProcessingOptions

# Configure your processor
config = {
    "processor_name": "AdvertisementRemover",
    "processing_enabled": True,
    "remove_ads": True,
    "remove_social": True,
    "transform_text": False,
}

service = ProcessingService(options=ProcessingOptions())

# Register custom processor (replaces duplicate detector for this example)
service.register_processor(CustomProcessor(config=config))

# Process content
result = service.process(content, source_url="https://example.com")

# Access results
print(f"Custom processor executed: {result.metrics.duplicates_removed} times")
print(f"Quality score: {result.content_quality_score}")
```

**As Custom Pipeline Stage (if adding new stage):**
```python
# First, you would need to extend ProcessingStage enum in backend/core/domain/content_processor.py
# Then create a new processor that returns the new stage value
# Then register it with ProcessingService

from backend.processor import ProcessingService, CustomProcessor
from backend.core.domain.content_processor import ProcessingStage

# Create custom processor that returns a custom stage
class MyCustomProcessor(IContentProcessor):
    def get_stage(self) -> ProcessingStage:
        return ProcessingStage.DUPLICATE_DETECTION  # Or request adding a new stage

# Then register and use
service = ProcessingService()
service.register_processor(MyCustomProcessor())
```

### Step 4: Add Tests (Optional but Recommended)

**File:** `backend/tests/unit/processor/test_custom_processor.py`

```python
"""
Unit tests for CustomProcessor implementation.
"""

import pytest
from backend.processor import ProcessingService, CustomProcessor, ProcessingOptions
from backend.processor.exceptions import ProcessingError


class TestCustomProcessor:
    """Test suite for CustomProcessor."""

    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        config = {
            "processor_name": "AdvertisementRemover",
            "processing_enabled": True,
            "remove_ads": True,
            "min_content_length": 10
        }
        return CustomProcessor(config=config)

    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return """
        <p>This is main content.</p>

        <p>Advertisement content here.</p>

        <p>More main content follows.</p>
        """

    def test_process_success(self, processor, sample_content):
        """Test successful processing."""
        options = ProcessingOptions()
        result, metadata = processor.process(sample_content, {}, options, {})

        assert "Advertisement content here" not in result
        assert metadata["custom_processed"] is True

    def test_empty_content_skip(self, processor):
        """Test that empty content is skipped."""
        options = ProcessingOptions()
        result, metadata = processor.process("", {}, options, {})

        assert result == ""
        assert metadata.get("custom_processed") is None  # Not set because skipped

    def test_disabled_processor(self, processor):
        """Test that disabled processor returns content unchanged."""
        config = {"processor_name": "TestProcessor", "processing_enabled": False}
        disabled_processor = CustomProcessor(config=config)

        options = ProcessingOptions()
        result, metadata = disabled_processor.process("test content", {}, options, {})

        assert result == "test content"
        assert metadata.get("custom_processed") is None

    def test_content_too_short(self, processor):
        """Test that short content is skipped."""
        config = {"min_content_length": 100}
        short_processor = CustomProcessor(config=config)

        options = ProcessingOptions()
        result, metadata = short_processor.process("short", {}, options, {})

        assert result == "short"
        assert metadata.get("custom_processed") is None  # Not set because skipped

    def test_content_too_long(self, processor):
        """Test that very long content is skipped."""
        config = {"max_content_length": 100}
        long_processor = CustomProcessor(config=config)

        options = ProcessingOptions(max_content_length=100)
        result, metadata = long_processor.process("a" * 200, {}, options, {})

        assert result == "a" * 200
        assert metadata.get("custom_processor_count") == 0

    def test_custom_processing_logic(self, processor):
        """Test custom processing logic."""
        config = {
            "processor_name": "PatternRemover",
            "processing_enabled": True,
            "remove_ads": True,
            "remove_social": False
        }
        pattern_processor = CustomProcessor(config=config)

        test_content = """
        <p>Main content here.</p>
        <p>Advertisement content here.</p>
        <p>Follow us on Twitter for more updates!</p>
        <p>More main content continues here.</p>
        """

        options = ProcessingOptions()
        result, metadata = pattern_processor.process(test_content, {}, options, {})

        assert "Advertisement content here" not in result
        assert "Follow us on Twitter for more updates!" in result  # social not removed

    def test_processing_metrics(self, processor):
        """Test that metrics are calculated correctly."""
        config = {
            "processor_name": "MetricsTestProcessor",
            "processing_enabled": True,
            "processing_multiplier": 2.0
        }
        metrics_processor = CustomProcessor(config=config)

        input_content = "Test content for metrics"
        processed_content = "Test content for metrics"

        options = ProcessingOptions()
        duration = 0.001

        metrics = metrics_processor.get_processing_metrics(
            len(input_content),
            len(processed_content),
            duration
        )

        assert metrics["input_length"] == len(input_content)
        assert metrics["output_length"] == len(processed_content)
        assert metrics["processor_name"] == "MetricsTestProcessor"
        assert metrics["duration_seconds"] == duration

    def test_validation_errors(self, processor):
        """Test that validation errors are returned."""
        config = {
            "require_specific_pattern": True,
            "processing_enabled": True
        }
        validation_processor = CustomProcessor(config=config)

        test_content = "This content has no pattern"
        options = ProcessingOptions()

        errors = validation_processor.validate(test_content, {}, options)

        assert "Content missing required pattern" in errors
        assert len(errors) > 0

    def test_strict_validation(self, processor):
        """Test strict validation behavior."""
        from backend.processor.exceptions import ProcessingValidationError

        config = {
            "processor_name": "StrictValidator",
            "processing_enabled": True
        }
        strict_processor = CustomProcessor(config=config)

        test_content = "Short"  # Very short content
        options = ProcessingOptions(minimum_content_length=10, strict_validation=True)

        with pytest.raises(ProcessingValidationError):
            strict_processor.process(test_content, {}, options, {})

    def test_lazy_validation(self, processor):
        """Test lenient validation behavior."""
        config = {
            "processor_name": "LazyValidator",
            "processing_enabled": True
        }
        lazy_processor = CustomProcessor(config=config)

        test_content = "Short"  # Very short content
        options = ProcessingOptions(minimum_content_length=10, strict_validation=False)

        result, metadata = lazy_processor.process(test_content, {}, options, {})

        assert result == "Short"
        assert metadata.get("custom_processed") is None  # Skipped due to length

    def test_memory_usage_estimation(self, processor):
        """Test memory usage estimation."""
        config = {
            "processor_name": "MemoryEstimator",
            "memory_multiplier": 1.5
        }
        memory_processor = CustomProcessor(config=config)

        content_length = 1000

        memory_estimate = memory_processor.get_memory_usage_estimate(content_length)

        assert memory_estimate == int(1000 * 2 * 1.5)  # 1000 bytes * 2x * 1.5x
        assert memory_estimate == 3000

    def test_stage_name(self, processor):
        """Test stage name."""
        assert processor.get_stage_name() == "Custom Processor"

    def test_estimate_processing_time(self, processor):
        """Test processing time estimation."""
        config = {
            "processor_name": "TimeEstimator",
            "processing_multiplier": 3.0
        }
        time_estimator = CustomProcessor(config=config)

        content_length = 1000

        time_estimate = time_estimator.estimate_processing_time(content_length, ProcessingOptions())

        assert time_estimate == 0.001 * 1000 * 3.0  # 1 second
        assert time_estimate == 3.0
```

### **Advanced: Processor Configuration**

Create a configuration class for your processor:

**File:** `backend/processor/implementations/your_processor.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomProcessorConfig:
    """Configuration for CustomProcessor."""

    processor_name: str = "CustomProcessor"
    processing_enabled: bool = True
    min_content_length: int = 10
    max_content_length: int = 10_000_000
    processing_multiplier: float = 1.0
    memory_multiplier: float = 1.0

    # Custom configuration
    remove_ads: bool = True
    remove_social: bool = False
    transform_text: bool = False
    title_case_conversion: bool = False
    require_specific_pattern: bool = False

    def validate(self) -> None:
        """Validate configuration."""
        if not self.processor_name:
            raise ValueError("processor_name cannot be empty")
        if self.min_content_length < 0:
            raise ValueError("min_content_length must be non-negative")
        if self.max_content_length < self.min_content_length:
            raise ValueError("max_content_length must be greater than min_content_length")
        if self.processing_multiplier < 0:
            raise ValueError("processing_multiplier must be non-negative")
        if self.memory_multiplier < 0:
            raise ValueError("memory_multiplier must be non-negative")


class CustomProcessor(IContentProcessor):
    """Custom processor with configuration."""

    def __init__(self, config: Optional[CustomProcessorConfig] = None):
        """
        Initialize processor with configuration.

        Args:
            config: Optional configuration object
        """
        self.config = config or CustomProcessorConfig()
        self.config.validate()  # Validate configuration

        # Use configuration values
        self.processing_enabled = self.config.processing_enabled
        self.processing_name = self.config.processor_name
```

**Usage with configuration:**
```python
from backend.processor import CustomProcessor, CustomProcessorConfig

# Create custom configuration
config = CustomProcessorConfig(
    processor_name="EnhancedDuplicateDetector",
    processing_enabled=True,
    min_content_length=100,
    similarity_threshold=0.85,
    remove_ads=True,
    remove_social=True,
    processing_multiplier=1.5,
    memory_multiplier=2.0
)

# Create processor with configuration
processor = CustomProcessor(config=config)

# Use with ProcessingService
service = ProcessingService()
service.register_processor(processor)
```

## Testing Your Implementation

### **Unit Tests**

```bash
# Run unit tests for your processor
python -m pytest backend/tests/unit/processor/test_custom_processor.py -v
```

### **Integration Tests**

```bash
# Run integration tests
python -m pytest backend/tests/integration/test_processor_integration.py -v
```

### **Quality Checks**

```bash
# Format code
python -m black backend/parser/implementations/your_processor.py

# Lint code
python -m ruff check backend/parser/implementations/your_processor.py

# Type check
python -m mypy backend/processor/implementations/your_parser.py
```

## Best Practices

### **1. Deterministic Processing**

```python
def process(self, content: str, metadata: Dict[str, Any], options: ProcessingOptions, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """
    Process content deterministically.

    Must always return same output for same input.

    Avoid:
    - Random number generation
    - Time-based decisions
    - External API calls
    - Database queries
    - File system operations
    """
    # Always use deterministic logic
```

### **2. Error Handling**

```python
def process(self, content: str, metadata: Dict[str, Any], options: ProcessingOptions, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    try:
        # Your processing logic
        pass
    except Exception as e:
        # Always wrap errors in ProcessorError
        raise ProcessorError(f"Custom processor failed: {str(e)}") from e
```

### **3. Performance Considerations**

```python
def should_skip_content(self, content: str, options: ProcessingOptions) -> bool:
    """Optimize by skipping unnecessary processing."""
    # Quick checks before expensive operations
    if not content or not content.strip():
        return True

    if len(content) > options.max_content_length:
        return True

    # Check processor-specific quick checks
    if not self._is_relevant_for_processor(content):
        return True

    return False
```

### **4. Type Hints**

```python
from typing import Optional, List, Dict, Any
from backend.core.domain.content_processor import ProcessingStage

def get_stage(self) -> ProcessingStage:
    """Return the processing stage this processor handles."""
    return ProcessingStage.DUPLICATE_DETECTION
```

### **5. Documentation**

```python
def process(
    self,
    content: str,
    metadata: Dict[str, Any],
    options: ProcessingOptions,
    context: Dict[str, Any]
) -> tuple[str, Dict[str, Any]]:
    """
    Process content according to the processor's specific logic.

    This method implements the core processing logic for the custom processor,
    extracting title, text content, metadata, and structured elements.

    Args:
        content: HTML content to parse (required)
        url: Optional URL for link classification and error reporting

    Returns:
        ParserResult object containing all extracted content

    Raises:
        ParserError: If parsing fails due to invalid HTML or other errors

    Example:
        >>> processor = CustomProcessor()
        >>> result, metadata = processor.parse("<html><body><h1>Test</h1></body></html>")
        >>> print(result.text_content)
        'Test'
    """
    # Your implementation
    pass
```

## Verification Checklist

Before considering your processor implementation complete, verify:

- [ ] Implements all methods from `IContentProcessor` interface
- [ ] All methods have proper type hints
- [ ] Comprehensive docstrings for public methods
- [ ] Error handling with `ProcessorError` exceptions
- [ ] Processing metrics in stage results
- [ ] Unit tests covering all methods
- [ ] Integration tests with real content
- [ ] Code formatted with Black
- Linting passes with Ruff
- Type checking passes with MyPy
- Added to module exports
- Works with `ProcessingService`
- Handles edge cases (empty content, invalid content, etc.)
- Processing is deterministic (same input = same output)

## Example Use Cases

### **Use Case 1: Industry-Specific Processor**

```python
class ECommerceProcessor(IParser):
    """Processor optimized for e-commerce websites."""

    def __init__(self, config: Optional[ECommerceConfig] = None):
        self.config = config or ECommerceConfig()
        self.stage = ProcessingStage.BOILERPLATE_REMOVAL

    def process(self, content: str, metadata: Dict[str, Any], options: ProcessingOptions, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process e-commerce content."""
        # E-commerce specific logic
        pass
```

### **Use Case 2: Language-Specific Processor**

```python
class LanguageAwareProcessor(IParser):
    """Processor with language-specific processing."""

    def __init__(self, config: Optional[LanguageConfig] = None):
        self.config = config or LanguageConfig()
        self.stage = ProcessingStage.TEXT_EXTRACTION

    def process(self, content: str, metadata: Dict[str, Any], options: ProcessingOptions, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process content with language awareness."""
        # Language-specific text processing
        pass
```

### **Use Case 3: Performance-Optimized Processor**

```python
class FastProcessor(IParser):
    """High-performance processor using optimized algorithms."""

    def __init__(self, config: Optional[FastConfig] = None):
        self.config = config or FastConfig()
        self.stage = ProcessingStage.WHITESPACE_NORMALIZATION

    def process(self, content: str, metadata: Dict[str, Any], options: ProcessingOptions, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process content with optimized algorithms."""
        # Fast processing using optimized string operations
        pass
```

## Conclusion

By following this guide, you can add new content processor implementations to the AI Website Intelligence Platform without modifying any existing code. This follows the **Open/Closed Principle** and ensures that:

1. ✅ Existing processors remain unchanged
2. ✅ New processors integrate seamlessly with `ProcessingService`
3. ✅ All processors follow the same `IContentProcessor` interface
4. ✅ Code remains maintainable and extensible
5. ✅ Testing and quality standards maintained
6. ✅ Processing remains deterministic and reproducible
7. ✅ Architecture scales with complexity

The Content Processor Foundation architecture is designed for extensibility, and new processors can be added as needed for specific use cases without compromising the existing codebase.