# ADR-0006: Clean Architecture for Parser Module

## Status
Accepted

## Context
Milestone 4 required implementing a robust HTML parsing foundation for the AI Website Intelligence Platform. The parser module needed to:

1. Support multiple parsing strategies (BeautifulSoup4, Trafilatura)
2. Enable easy extension with new parsers
3. Provide clear separation of concerns
4. Support comprehensive testing
5. Scale to future complexity (ML integration, AI features)

Traditional layered architectures often lead to:
- Tight coupling between layers
- Business logic mixed with infrastructure concerns
- Difficult testing of individual components
- Scalability limitations as complexity increases

Clean Architecture provides a systematic approach to these challenges through dependency inversion and clear boundaries.

## Decision
Implement **Clean Architecture** for the parser module with distinct layers and dependency inversion:

### Architecture Layers

**1. Domain Layer (Core Business Logic)**
- **Location:** `backend/core/domain/parser.py`, `backend/core/interfaces/parser.py`
- **Components:**
  - `IParser` interface (abstract contract)
  - Domain models: `ParserResult`, `MetaData`, `Heading`, `Link`, `Image`, `Script`, `Stylesheet`, `ParsingMetrics`
- **Dependencies:** None (most inner layer)
- **Responsibility:** Define business entities and contracts

**2. Application Layer (Orchestration)**
- **Location:** `backend/parser/parser_service.py`
- **Components:**
  - `ParserService` - Parser orchestration and strategy selection
- **Dependencies:** Domain Layer (`IParser`, domain models)
- **Responsibility:** Orchestration and coordination only (no business logic)

**3. Infrastructure Layer (Implementation)**
- **Location:** `backend/parser/implementations/`
- **Components:**
  - `BeautifulSoupParser` - DOM-based HTML parsing
  - `TrafilaturaParser` - Content-focused extraction
  - Future parsers (lxml, html5lib, custom)
- **Dependencies:** Domain Layer (`IParser` interface)
- **Responsibility:** Technical implementation details

**4. Presentation Layer (Future)**
- **Location:** Future FastAPI endpoints
- **Components:** API routes, DTOs, controllers
- **Dependencies:** Application Layer (`ParserService`)
- **Responsibility:** HTTP/API concerns

### Dependency Rule
```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                            │
│                  (Future: FastAPI Endpoints)                     │
└─────────────────────────────────────────────────────────────────┘
                          ▲ Depends on
                          │
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│                      ParserService                               │
└─────────────────────────────────────────────────────────────────┘
                          ▲ Depends on
                          │
┌─────────────────────────────────────────────────────────────────┐
│                       Domain Layer                                │
│              Domain Models + IParser Interface                    │
└─────────────────────────────────────────────────────────────────┘
                          ▲ Depends on
                          │
┌─────────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                             │
│        Parser Implementations (BeautifulSoup, Trafilatura)       │
└─────────────────────────────────────────────────────────────────┘
```

**Key Principle:** Dependencies point inward. Outer layers depend on inner layers, never vice versa.

## Consequences

### Positive
- **Testability:** Each layer can be tested independently with mocks
- **Maintainability:** Clear separation of concerns makes code easier to understand and modify
- **Extensibility:** New parsers can be added without modifying existing code (Open/Closed Principle)
- **Scalability:** Architecture scales well as complexity increases (ML, AI features in future milestones)
- **Flexibility:** Different implementations can be swapped without affecting business logic
- **Dependency Inversion:** High-level modules depend on abstractions, not concrete implementations

### Negative
- **Complexity:** Additional layers and abstractions increase initial complexity
- **Learning Curve:** Team members need to understand Clean Architecture principles
- **Overhead:** Slight performance overhead from additional abstraction layers
- **Boilerplate**: More files and interfaces required compared to simple implementations

### Risks
- Violation of dependency rules leading to tight coupling
- Business logic creeping into orchestration layer (ParserService)
- Infrastructure concerns leaking into domain layer
- Over-engineering for simple use cases

### Mitigations
- Clear documentation of layer responsibilities
- Regular code reviews to enforce architectural boundaries
- Comprehensive test coverage validates separation of concerns
- Code quality tools enforce dependency rules (MyPy, Ruff)
- Explicit documentation of ParserService anti-patterns to avoid

## Implementation Details

### Domain Layer - IParser Interface
```python
from abc import ABC, abstractmethod
from typing import Optional

class IParser(ABC):
    """Abstract contract for HTML parsers."""

    @abstractmethod
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        """Parse HTML content and return structured result."""
        pass

    @abstractmethod
    def extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        pass

    # ... other abstract methods
```

### Domain Layer - Domain Models
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ParserResult:
    """Complete parsing result with all extracted content."""
    url: str
    title: str
    content: str
    text_content: str
    metadata: MetaData
    headings: List[Heading]
    links: List[Link]
    images: List[Image]
    scripts: List[Script]
    stylesheets: List[Stylesheet]
    metrics: ParsingMetrics

@dataclass
class MetaData:
    """Structured metadata extracted from HTML."""
    title: str
    description: Optional[str]
    keywords: List[str]
    canonical_url: Optional[str]
    og_data: Dict[str, str]
    twitter_data: Dict[str, str]
    # ... additional fields
```

### Application Layer - ParserService
```python
class ParserService:
    """
    Parser orchestration service.

    Responsibilities:
    - Parser selection strategy
    - Automatic fallback handling
    - Performance metrics collection
    - Error handling and recovery

    Anti-patterns to avoid:
    - Business logic (contact extraction, technology detection)
    - Domain-specific content analysis
    - Industry-specific extraction rules
    """

    def __init__(
        self,
        primary_parser: IParser,
        fallback_parser: Optional[IParser] = None,
        enable_fallback: bool = True
    ):
        self.primary_parser = primary_parser
        self.fallback_parser = fallback_parser
        self.enable_fallback = enable_fallback
        self.metrics = ParsingMetricsCollection()

    def parse(
        self,
        html: str,
        url: Optional[str] = None,
        parser_type: Optional[str] = None
    ) -> ParserResult:
        """Parse HTML with strategy selection and fallback."""
        # Orchestration logic only - no business logic
```

### Infrastructure Layer - Parser Implementations
```python
class BeautifulSoupParser(IParser):
    """
    BeautifulSoup4 implementation of IParser.

    Responsibilities:
    - DOM-based HTML parsing
    - Comprehensive metadata extraction
    - Structured content extraction

    Infrastructure concerns only - no business logic.
    """

    def __init__(self, config: Optional[BeautifulSoupConfig] = None):
        self.config = config or BeautifulSoupConfig()
        # Setup BeautifulSoup-specific resources

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        """Implement IParser interface using BeautifulSoup4."""
        # BeautifulSoup-specific implementation
        pass

class TrafilaturaParser(IParser):
    """Trafilatura implementation of IParser."""
    # Similar structure for Trafilatura implementation
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- **ParserService**: Parser orchestration only
- **BeautifulSoupParser**: DOM-based parsing only
- **TrafilaturaParser**: Content extraction only
- **Domain Models**: Data representation only

### Open/Closed Principle (OCP)
- New parsers can be added by implementing `IParser` interface
- No existing code needs modification for new parser implementations
- `ParserService` works with any `IParser` implementation

### Liskov Substitution Principle (LSP)
- All parser implementations are interchangeable
- Any `IParser` implementation can replace another without breaking the system
- Consistent behavior across all parser implementations

### Interface Segregation Principle (ISP)
- `IParser` interface is focused and cohesive
- No client is forced to depend on methods it doesn't use
- Clear separation of different concerns (parsing vs. content extraction)

### Dependency Inversion Principle (DIP)
- High-level modules (`ParserService`) depend on abstractions (`IParser`)
- Low-level modules (`BeautifulSoupParser`) implement abstractions
- No dependency on concrete implementations in business logic

## Future Milestone Integration

### Milestone 5: Data Processing
- New Application Layer service: `DataProcessingService`
- Domain models extended with processing metadata
- Infrastructure layer: pandas, numpy implementations
- Clean separation maintained

### Milestone 6: ML Integration
- New Domain Layer models: `ContentClassification`, `QualityScore`
- New Application Layer service: `MLProcessingService`
- Infrastructure layer: scikit-learn, TensorFlow implementations
- No modification to existing parser infrastructure

### Milestone 7: Advanced Features
- Caching layer in Infrastructure Layer
- Parallel processing in Application Layer
- Domain models extended with caching metadata
- Clean Architecture maintained throughout

## Testing Strategy

### Unit Tests (Layer Isolation)
```python
# Domain Layer - Test domain models independently
def test_parser_result_creation():
    result = ParserResult(
        url="https://example.com",
        title="Example",
        content="<html>...</html>",
        # ... other fields
    )
    assert result.url == "https://example.com"
    assert result.title == "Example"

# Application Layer - Test orchestration with mocked dependencies
def test_parser_service_with_fallback():
    mock_primary = Mock(spec=IParser)
    mock_fallback = Mock(spec=IParser)

    mock_primary.parse.side_effect = ParserError("Primary failed")
    mock_fallback.parse.return_value = ParserResult(...)

    service = ParserService(
        primary_parser=mock_primary,
        fallback_parser=mock_fallback
    )

    result = service.parse(html, url="https://example.com")
    assert result is not None
    mock_fallback.parse.assert_called_once()
```

### Integration Tests (Cross-layer)
```python
def test_parser_service_integration():
    """Test complete flow from service to parser implementation."""
    service = ParserService(
        primary_parser=BeautifulSoupParser(),
        fallback_parser=TrafilaturaParser()
    )

    html = "<html><head><title>Test</title></head></html>"
    result = service.parse(html, url="https://example.com")

    assert result.title == "Test"
    assert result.metrics.parser_used in ["BeautifulSoupParser", "TrafilaturaParser"]
```

## References
- Clean Architecture by Robert C. Martin
- SOLID Principles
- Domain Models: `backend/core/domain/parser.py`
- Interfaces: `backend/core/interfaces/parser.py`
- Service Layer: `backend/parser/parser_service.py`
- Implementations: `backend/parser/implementations/`

## Related Decisions
- ADR-0004: Use BeautifulSoup4 and Trafilatura as Dual Parser Strategy
- ADR-0005: Strategy Pattern for Parser Selection
- ADR-0007: ParserService Orchestration Focus

## Implementation Status
✅ Implemented in Milestone 4
- Domain Layer: Complete with all models and interfaces
- Application Layer: ParserService with orchestration logic
- Infrastructure Layer: BeautifulSoupParser and TrafilaturaParser implementations
- Testing: Comprehensive unit and integration tests (2,400+ lines)
- Documentation: Complete architecture documentation

## Examples

### Adding New Parser Without Modifying Existing Code
```python
# 1. Create new implementation in Infrastructure Layer
class CustomParser(IParser):
    """Custom parser for specific use case."""
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # Custom implementation
        pass

# 2. Use immediately through existing Application Layer
service = ParserService(
    primary_parser=CustomParser(),  # No code modification needed!
    fallback_parser=BeautifulSoupParser()
)

# 3. Works seamlessly with existing Domain Layer
result = service.parse(html, url="https://example.com")
# Returns ParserResult with same structure as other parsers
```

### Maintaining Clean Boundaries
```python
# ❌ WRONG: Business logic in ParserService
class ParserService:
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        result = self.primary_parser.parse(html, url)
        # DON'T add business logic here:
        # if "product" in result.title.lower():
        #     result.metadata.category = "e-commerce"
        return result

# ✅ CORRECT: Business logic in separate service
class ECommerceAnalysisService:
    """Separate service for e-commerce business logic."""
    def analyze_product_page(self, result: ParserResult) -> ProductInfo:
        if "product" in result.title.lower():
            return ProductInfo(category="e-commerce")
        return ProductInfo(category="unknown")
```

## Lessons Learned

1. **Start Simple, Add Complexity Gradually**: Initial implementation focused on core layers, added sophistication over time
2. **Documentation is Critical**: Clear documentation of layer responsibilities prevents architectural drift
3. **Tests Validate Architecture**: Comprehensive test coverage ensures separation of concerns is maintained
4. **Review Regularly**: Code reviews help catch architectural violations early
5. **Balance Principles with Pragmatism**: Sometimes pragmatic decisions override perfect architectural purity

## Risks for Future Milestones

1. **Architectural Drift**: Business logic creeping into orchestration layer
2. **Interface Bloat**: IParser interface becoming too broad
3. **Dependency Violations**: Outer layers depending on inner layers
4. **Testing Gaps**: Insufficient integration testing across layers
5. **Performance Overhead**: Abstraction layers impacting performance at scale

## Mitigation Strategies

1. **Regular Architecture Reviews**: Dedicated time to review architectural compliance
2. **Code Quality Tools**: MyPy, Ruff to enforce dependency rules
3. **Documentation Updates**: Keep architecture docs synchronized with implementation
4. **Performance Monitoring**: Track performance impact of abstractions
5. **Team Training**: Regular training on Clean Architecture principles