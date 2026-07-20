# Content Processor - Public API Documentation

## Overview

The Content Processor Module provides a Clean Architecture-based content processing system that transforms parsed HTML content into clean, normalized, structured content. This document describes the public API for developers who need to integrate with the content processing system.

## Module Structure

```
backend/processor/
├── __init__.py              # Public API exports
├── exceptions.py            # Processor-specific exceptions
├── processor_service.py    # Orchestration service
└── implementations/
    ├── __init__.py         # Processor implementations exports
    ├── whitespace_normalizer.py      # Whitespace normalization
    ├── unicode_normalizer.py         # Unicode normalization
    ├── html_entity_decoder.py         # HTML entity decoding
    ├── boilerplate_remover.py         # Boilerplate removal
    ├── navigation_remover.py         # Navigation/footer removal
    ├── duplicate_detector.py         # Duplicate detection
    ├── paragraph_reconstructor.py     # Paragraph reconstruction
    ├── heading_associator.py         # Heading association
    ├── reading_order_reconstructor.py # Reading order reconstruction
    ├── metadata_cleaner.py            # Metadata cleanup
    └── content_validator.py           # Content validation

backend/core/
├── domain/
│   └── content_processor.py     # Domain models (ProcessingResult, etc.)
└── interfaces/
    └── content_processor.py      # IContentProcessor interface definition
```

## Public API Exports

### **Main Entry Point**

```python
from backend.processor import (
    # Service
    ProcessingService,

    # Processors
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

    # Exceptions
    ProcessorError,
    ProcessorNotAvailableError,
    ProcessingTimeoutError,
    ProcessingValidationError,

    # Domain models
    ProcessingResult,
    ProcessingMetrics,
    ContentSection,
    TextSegment,
    NormalizedText,
    ContentMetadata,
    ProcessingOptions,
    ProcessingStage,
    ProcessingStageResult,
)

# Core interface
from backend.core.interfaces import IContentProcessor
```

---

## Classes

### **ProcessingService**

The main orchestration service for content processing operations.

#### **Constructor**

```python
def __init__(
    options: Optional[ProcessingOptions] = None,
    processors: Optional[List[IContentProcessor]] = None,
    enable_timeout: bool = True
) -> None
```

**Parameters:**
- `options`: Processing configuration options (default: `ProcessingOptions()`)
- `processors`: List of processors to use (default: 11 default processors)
- `enable_timeout`: Whether to enable timeout protection (default: `True`)

**Example:**
```python
from backend.processor import ProcessingService, ProcessingOptions

# Create service with default options
service = ProcessingService()

# Create service with custom options
options = ProcessingOptions(
    enable_whitespace_normalization=True,
    enable_unicode_normalization=True,
    min_duplicate_length=50,
    similarity_threshold=0.9
)
service = ProcessingService(options=options)
```

#### **Methods**

##### **process**

Processes content through the complete pipeline.

```python
def process(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    source_url: Optional[str] = None
) -> ProcessingResult
```

**Parameters:**
- `content`: Input content to process (required)
- `metadata`: Optional content metadata (default: `None`)
- `source_url`: Optional source URL for tracking (default: `None`)

**Returns:** `ProcessingResult` object with processed content

**Raises:**
- `ProcessorError`: If processing fails
- `ProcessingTimeoutError`: If processing times out
- `ProcessingValidationError`: If validation fails

**Example:**
```python
# Process content with default pipeline
result = service.process(content, source_url="https://example.com")

# Access processed content
print(f"Original: {result.original_content}")
print(f"Normalized: {result.normalized_text.normalized_text}")
print(f"Quality score: {result.content_quality_score}")
```

##### **register_processor**

Register a processor for a specific processing stage.

```python
def register_processor(processor: IContentProcessor) -> None
```

**Parameters:**
- `processor`: Processor instance to register

**Example:**
```python
from backend.processor import ProcessingService
from backend.processor.implementations import WhitespaceNormalizer

service = ProcessingService()
service.register_processor(WhitespaceNormalizer())
```

##### **unregister_processor**

Unregister a processor by stage.

```python
def unregister_processor(stage: ProcessingStage) -> None
```

**Parameters:**
- `stage`: Processing stage to unregister

**Example:**
```python
from backend.processor import ProcessingService, ProcessingStage

service = ProcessingService()
service.unregister_processor(ProcessingStage.WHITESPACE_NORMALIZATION)
```

##### **get_processor**

Get a processor by stage.

```python
def get_processor(stage: ProcessingStage) -> IContentProcessor
```

**Parameters:**
- `stage`: Processing stage

**Returns:** Processor instance

**Raises:** `ProcessorNotAvailableError` if processor not available

**Example:**
```python
from backend.processor import ProcessingService, ProcessingStage

service = ProcessingService()
processor = service.get_processor(ProcessingStage.UNICODE_NORMALIZATION)
print(f"Processor: {processor.get_stage_name()}")
```

##### **get_available_stages**

Get list of available processing stages.

```python
def get_available_stages() -> List[ProcessingStage]
```

**Returns:** List of `ProcessingStage` enum values

**Example:**
```python
stages = service.get_available_stages()
print(f"Available stages: {len(stages)}")  # 11 stages
```

##### **get_metrics**

Get performance metrics for the service.

```python
def get_metrics() -> Dict[str, Any]
```

**Returns:** Dictionary with service-level metrics:
- `total_processing_count`: Total number of processing operations
- `successful_processing_count`: Number of successful operations
- `failed_processing_count`: Number of failed operations
- `success_rate`: Success rate as percentage
- `registered_processors`: List of registered processor stages

**Example:**
```python
metrics = service.get_metrics()
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Total processed: {metrics['total_processing_count']}")
```

##### **enable_stage**

Enable or disable a processing stage.

```python
def enable_stage(stage: ProcessingStage, enabled: bool = True) -> None
```

**Parameters:**
- `stage`: Processing stage to enable/disable
- `enabled`: Whether to enable the stage (default: `True`)

**Example:**
```python
from backend.processor import ProcessingService, ProcessingStage

service = ProcessingService()
service.enable_stage(ProcessingStage.DUPLICATE_DETECTION, enabled=False)
```

##### **reset_metrics**

Reset performance metrics.

```python
def reset_metrics() -> None
```

**Example:**
```python
service.reset_metrics()
```

---

### **IContentProcessor Interface**

The base interface that all processor implementations must follow.

```python
class IContentProcessor(ABC):
    @abstractmethod
    def get_stage(self) -> ProcessingStage:
        """Return the processing stage this processor handles."""
        pass

    @abstractmethod
    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Process content according to the processor's specific logic."""
        pass

    @abstractmethod
    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> list[str]:
        """Validate content before processing."""
        pass

    @abstractmethod
    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
    ) -> Dict[str, Any]:
        """Calculate processing metrics for this stage."""
        pass
```

---

## Domain Models

### **ProcessingOptions**

Configuration options for content processing.

```python
@dataclass
class ProcessingOptions:
    # Stage enablement (11 stages)
    enable_whitespace_normalization: bool = True
    enable_unicode_normalization: bool = True
    enable_html_entity_decoding: bool = True
    enable_boilerplate_removal: bool = True
    enable_navigation_footer_removal: bool = True
    enable_duplicate_detection: bool = True
    enable_paragraph_reconstruction: bool = True
    enable_heading_association: bool = True
    enable_reading_order_reconstruction: bool = True
    enable_metadata_cleanup: bool = True
    enable_validation: bool = True

    # Whitespace normalization options
    normalize_newlines: bool = True
    collapse_multiple_spaces: bool = True
    trim_whitespace: bool = True

    # Unicode normalization options
    unicode_form: str = "NFC"  # NFC, NFD, NFKC, NFKD
    normalize_quotes: bool = True
    normalize_dashes: bool = True

    # Boilerplate removal options
    remove_comments: bool = True
    remove_advertisements: bool = True
    remove_social_media_widgets: bool = True

    # Navigation/footer removal options
    remove_navigation_menus: bool = True
    remove_footers: bool = True
    remove_sidebars: bool = True

    # Duplicate detection options
    min_duplicate_length: int = 50
    similarity_threshold: float = 0.9

    # Paragraph reconstruction options
    min_paragraph_length: int = 10
    max_paragraph_length: int = 2000

    # Heading association options
    max_heading_distance: int = 5

    # Reading order reconstruction options
    respect_html_structure: bool = True
    fallback_to_visual_order: bool = False

    # Validation options
    strict_validation: bool = True
    allow_empty_content: bool = False
    minimum_content_length: int = 100

    # Performance options
    timeout_seconds: int = 30
    max_content_length: int = 10_000_000
```

**Example:**
```python
from backend.processor import ProcessingOptions

options = ProcessingOptions(
    enable_duplicate_detection=True,
    min_duplicate_length=100,
    similarity_threshold=0.85,
    strict_validation=False,
    timeout_seconds=60
)

service = ProcessingService(options=options)
```

### **ProcessingResult**

The main result object containing all processed content.

```python
@dataclass
class ProcessingResult:
    source_url: str                          # Source URL
    original_content: str                   # Original input content
    normalized_text: NormalizedText          # Normalized content
    content_sections: List[ContentSection]     # Content sections
    text_segments: List[TextSegment]           # Text segments
    metadata: ContentMetadata                  # Cleaned metadata
    metrics: ProcessingMetrics                  # Performance metrics

    # Processing status
    processing_complete: bool = True
    processing_errors: List[str] = []
    processing_warnings: List[str] = []

    # Quality indicators
    content_quality_score: float = 0.0
    determinism_score: float = 1.0              # Should always be 1.0

    # Timestamps
    processing_started: Optional[datetime] = None
    processing_completed: Optional[datetime] = None

    # Helper methods
    def calculate_quality_score(self) -> float
    def get_effective_content(self) -> str
    def get_content_by_section_type(self, section_type: str) -> List[ContentSection]
    def get_reading_order_text(self) -> str
```

**Example:**
```python
result = service.process(content)

# Access processed content
print(f"Original length: {len(result.original_content)}")
print(f"Normalized length: {len(result.normalized_text.normalized_text)}")
print(f"Quality score: {result.content_quality_score}")

# Get effective content (non-boilerplate)
effective_content = result.get_effective_content()

# Get content by section
content_sections = result.get_content_by_section_type("content")

# Get reading order text
reading_text = result.get_reading_order_text()
```

### **ProcessingStage**

Enumeration of processing stages in the pipeline.

```python
class ProcessingStage(Enum):
    WHITESPACE_NORMALIZATION = "whitespace_normalization"
    UNICODE_NORMALIZATION = "unicode_normalization"
    HTML_ENTITY_DECODING = "html_entity_decoding"
    BOILERPLATE_REMOVAL = "boilerplate_removal"
    NAVIGATION_FOOTER_REMOVAL = "navigation_footer_removal"
    DUPLICATE_DETECTION = "duplicate_detection"
    PARAGRAPH_RECONSTRUCTION = "paragraph_reconstruction"
    HEADING_ASSOCIATION = "heading_association"
    READING_ORDER_RECONSTRUCTION = "reading_order_reconstruction"
    METADATA_CLEANUP = "metadata_cleanup"
    VALIDATION = "validation"
```

**Example:**
```python
from backend.core.domain.content_processor import ProcessingStage

print(ProcessingStage.WHITESPACE_NORMALIZATION.value)
# "whitespace_normalization"

# Check if stage is available
if ProcessingStage.DUPLICATE_DETECTION in service.get_available_stages():
    print("Duplicate detection is available")
```

### **TextSegment**

A segment of text with associated metadata.

```python
@dataclass
class TextSegment:
    text: str                               # Segment text
    segment_type: str                        # "paragraph", "heading", "list", etc.
    position: int                            # Position in document
    start_index: int                         # Start index in content
    end_index: int                           # End index in content
    level: Optional[int] = None               # For headings (1-6)

    # Classification
    is_duplicate: bool = False
    is_boilerplate: bool = False
    is_navigation: bool = False
    is_footer: bool = False

    # Parent-child relationships
    parent_heading: Optional[int] = None     # Position of parent heading
    children_segments: List[int] = []        # Positions of child segments

    # Quality metrics
    word_count: int = 0
    sentence_count: int = 0
    character_count: int = 0
    average_word_length: float = 0.0
```

**Example:**
```python
segment = TextSegment(
    text="This is a paragraph.",
    segment_type="paragraph",
    position=0,
    start_index=0,
    end_index=23,
    word_count=5,
    sentence_count=1,
    character_count=23,
    average_word_length=4.6
)
```

### **ContentSection**

A logical section of content with related text segments.

```python
@dataclass
class ContentSection:
    section_id: str                         # Section identifier
    heading: Optional[TextSegment]          # Section heading
    segments: List[TextSegment]            # Text segments in section
    position: int                            # Position in document
    section_type: str = "content"            # "content", "navigation", "footer"

    # Metrics
    word_count: int = 0
    sentence_count: int = 0
    estimated_reading_time_minutes: float = 0.0

    def calculate_metrics(self) -> None
```

**Example:**
```python
heading = TextSegment(
    text="Introduction",
    segment_type="heading",
    level=1,
    position=0,
    start_index=0,
    end_index=12
)

section = ContentSection(
    section_id="introduction",
    heading=heading,
    segments=[paragraph1, paragraph2],
    position=0,
    section_type="content"
)

section.calculate_metrics()
print(f"Reading time: {section.estimated_reading_time_minutes:.1f} minutes")
```

### **NormalizedText**

Normalized and processed text content with statistics.

```python
@dataclass
class NormalizedText:
    original_text: str                      # Original text
    normalized_text: str                    # Processed text

    # Statistics
    original_word_count: int = 0
    normalized_word_count: int = 0
    word_reduction: int = 0
    word_reduction_percentage: float = 0.0

    original_char_count: int = 0
    normalized_char_count: int = 0
    char_reduction: int = 0
    char_reduction_percentage: float = 0.0

    # Processing status
    whitespace_normalized: bool = False
    unicode_normalized: bool = False
    html_entities_decoded: bool = False
    duplicates_removed: bool = False
    boilerplate_removed: bool = False

    # Validation status
    is_valid: bool = True
    validation_errors: List[str] = []

    def calculate_statistics(self) -> None
```

**Example:**
```python
normalized_text = NormalizedText(
    original_text="Original text here.",
    normalized_text="Original text here."
)

normalized_text.calculate_statistics()
print(f"Word reduction: {normalized_text.word_reduction_percentage:.2f}%")
```

### **ContentMetadata**

Cleaned and normalized metadata.

```python
@dataclass
class ContentMetadata:
    title: str
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    language: Optional[str] = None
    content_type: Optional[str] = None
    canonical_url: Optional[str] = None

    # Open Graph data
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None

    # Twitter Card data
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_card_type: Optional[str] = None

    # Processing metadata
    metadata_normalized: bool = False
    duplicates_removed: bool = False
    validation_passed: bool = True

    def normalize(self) -> ContentMetadata
```

**Example:**
```python
metadata = ContentMetadata(
    title="Example Page",
    description="An example page",
    keywords=["test", "example", "page"]
)

metadata = metadata.normalize()
print(f"Normalized: {metadata.metadata_normalized}")
```

### **ProcessingMetrics**

Performance and quality metrics for content processing.

```python
@dataclass
class ProcessingMetrics:
    total_processing_duration_seconds: float = 0.0
    input_content_length: int = 0
    output_content_length: int = 0
    content_compression_ratio: float = 0.0

    # Stage metrics
    stage_results: List[ProcessingStageResult] = field(default_factory=list)

    # Content metrics
    whitespace_normalized_count: int = 0
    unicode_normalized_count: int = 0
    html_entities_decoded: int = 0
    boilerplate_sections_removed: int = 0
    navigation_sections_removed: int = 0
    duplicates_removed: int = 0
    paragraphs_reconstructed: int = 0
    headings_associated: int = 0
    reading_order_segments: int = 0

    # Validation metrics
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    validation_passed: bool = True

    # Performance metrics
    memory_usage_bytes: int = 0
    cpu_usage_percent: float = 0.0

    def add_stage_result(self, result: ProcessingStageResult) -> None
```

**Example:**
```python
metrics = ProcessingMetrics()
metrics.total_processing_duration_seconds = 1.23
metrics.input_content_length = 1000
metrics.output_content_length = 800
metrics.content_compression_ratio = 0.8

print(f"Processing time: {metrics.total_processing_duration_seconds:.2f}s")
print(f"Compression: {metrics.content_compression_ratio:.2%}")
```

---

## Exceptions

### **ProcessorError**

Base exception for processor-related errors.

```python
class ProcessorError(Exception):
    """Base exception for processor errors."""
    pass
```

### **ProcessorNotAvailableError**

Raised when a requested processor is not available.

```python
class ProcessorNotAvailableError(ProcessorError):
    """Raised when a processor is not available."""
    pass
```

### **ProcessingTimeoutError**

Raised when processing operation times out.

```python
class ProcessingTimeoutError(ProcessorError):
    """Raised when processing times out."""
    pass
```

### **ProcessingValidationError**

Raised when content validation fails.

```python
class ProcessingValidationError(ProcessorError):
    """Raised when content validation fails."""
    pass
```

---

## Usage Examples

### **Basic Content Processing**

```python
from backend.processor import ProcessingService

# Create service with default options
service = ProcessingService()

# Process content
content = """
<p>This   is    a   test.</p>

<p>Another  paragraph  with  extra  spaces.</p>
"""

result = service.process(content)

# Access results
print(f"Original: {len(result.original_content)} characters")
print(f"Processed: {len(result.normalized_text.normalized_text)} characters")
print(f"Quality score: {result.content_quality_score}")
print(f"Processing time: {result.metrics.total_processing_duration_seconds:.3f}s")
```

### **Custom Configuration**

```python
from backend.processor import ProcessingService, ProcessingOptions

# Configure processing
options = ProcessingOptions(
    enable_duplicate_detection=True,
    min_duplicate_length=100,
    similarity_threshold=0.85,
    strict_validation=False,
    timeout_seconds=60
)

service = ProcessingService(options=options)
result = service.process(content)
```

### **Stage Control**

```python
from backend.processor import ProcessingService, ProcessingStage

service = ProcessingService()

# Disable duplicate detection
service.enable_stage(ProcessingStage.DUPLICATE_DETECTION, enabled=False)

# Process content
result = service.process(content)
```

### **Custom Pipeline**

```python
from backend.processor import ProcessingService, ProcessingOptions
from backend.processor.implementations import (
    WhitespaceNormalizer,
    UnicodeNormalizer,
    HTMLEntityDecoder
)

# Create custom pipeline
options = ProcessingOptions()
service = ProcessingService(options=options)

# Register custom processors
service.register_processor(WhitespaceNormalizer())
service.register_processor(UnicodeNormalizer())
service.register_processor(HTMLEntityDecoder())

# Process with custom pipeline
result = service.process(content)
```

### **Error Handling**

```python
from backend.processor import ProcessingService
from backend.processor.exceptions import (
    ProcessorError,
    ProcessorNotAvailableError,
    ProcessingTimeoutError,
    ProcessingValidationError,
)

service = ProcessingService()

try:
    result = service.process(content)
except ProcessingNotAvailableError as e:
    print(f"Processor not available: {e}")
except ProcessingTimeoutError as e:
    print(f"Processing timeout: {e}")
except ProcessingValidationError as e:
    print(f"Validation failed: {e.validation_errors}")
except ProcessorError as e:
    print(f"Processing error: {e}")
```

### **Metrics Collection**

```python
from backend.processor import ProcessingService

service = ProcessingService()

# Process several documents
for content in content_documents:
    service.process(content)

# Get performance metrics
metrics = service.get_metrics()
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Total processed: {metrics['total_processing_count']}")
print(f"Successful: {metrics['successful_processing_count']}")
print(f"Failed: {metrics['failed_processing_count']}")
```

### **Analysis of Results**

```python
# Analyze processed content
result = service.process(content)

# Check content quality
if result.content_quality_score > 0.8:
    print("High quality content")
elif result.content_quality_score > 0.5:
    print("Medium quality content")
else:
    print("Low quality content")

# Check what was removed
print(f"Duplicate paragraphs removed: {result.metrics.duplicates_removed}")
print(f"Boilerplate sections removed: {result.metrics.boilerplate_sections_removed}")
print(f"Navigation sections removed: {result.metrics.navigation_sections_removed}")

# Check effective content
effective = result.get_effective_content()
print(f"Effective content: {len(effective)} characters")

# Get content by type
main_content = result.get_content_by_section_type("content")
print(f"Main content sections: {len(main_content)}")
```

---

## Integration Guidelines

### **With Parser Module**

```python
from backend.parser import ParserService, BeautifulSoupParser
from backend.processor import ProcessingService, ProcessingOptions

# Create services
parser = ParserService(primary_parser=BeautifulSoupParser())
processor = ProcessingService(options=ProcessingOptions())

# Crawl and parse
parser_result = parser.parse(html, url="https://example.com")

# Process parsed content
processing_result = processor.process(
    parser_result.text_content,
    metadata=parser_result.metadata.__dict__,
    source_url=parser_result.url
)

print(f"Title: {processing_result.metadata.title}")
print(f"Processed content: {processing_result.normalized_text.normalized_text[:100]}...")
```

### **Quality Assessment**

```python
# Process content
result = service.process(content)

# Comprehensive quality assessment
print(f"Content quality: {result.content_quality_score:.2f}")
print(f"Determinism: {result.determinism_score:.2f}")
print(f"Validation passed: {result.metrics.validation_passed}")
print(f"Original words: {result.normalized_text.original_word_count}")
print(f"Processed words: {result.normalized_text.normalized_word_count}")
print(f"Reduction: {result.normalized_text.word_reduction_percentage:.1f}%")
```

---

## Best Practices

### **Processor Configuration**

1. **Use appropriate similarity thresholds:**
   - High threshold (0.95+): Strict duplicate detection
   - Medium threshold (0.85-0.95): Balanced detection
   - Low threshold (0.75-0.85): Permissive detection

2. **Adjust paragraph length constraints:**
   - Short paragraphs: 10-50 characters (headers, introductions)
   - Normal paragraphs: 50-500 characters
   - Long paragraphs: 500-2000 characters

3. **Timeout settings:**
   - Fast processing: 10-30 seconds
   - Normal processing: 30-60 seconds
   - Large documents: 60-120 seconds

### **Error Handling**

- Always handle `ProcessorError` exceptions
- Implement appropriate fallback strategies
- Log processing failures for debugging
- Consider retry mechanisms for transient failures
- Use validation to catch issues early

### **Performance**

- Use appropriate timeout settings
- Monitor metrics for performance optimization
- Consider caching for repeated content
- Process large content in chunks if needed

### **Content Quality**

- Set appropriate minimum content lengths
- Use strict validation for critical applications
- Monitor quality scores for optimization
- Review validation warnings for improvement

---

## API Versioning

Current version: `1.0.0`

**Stability:** Stable for production use

**Breaking Changes:**
- API changes will increment major version number
- Backwards compatible changes increment minor version number
- Bug fixes increment patch version number

---

## Support

For issues, questions, or contributions:
- Review the architecture documentation: `backend/docs/CONTENT_PROCESSOR_ARCHITECTURE.md`
- Check extension guide: `backend/docs/CONTENT_PROCESSOR_EXTENSION_GUIDE.md`
- Review test cases for usage examples: `backend/tests/unit/processor/`