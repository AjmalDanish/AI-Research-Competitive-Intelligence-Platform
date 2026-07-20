# ADR-0005: Strategy Pattern for Parser Selection and Execution

## Status
Accepted

## Context
The Parser Foundation needed to support multiple HTML parsing implementations with different strengths:

- **BeautifulSoup4**: Comprehensive metadata extraction, flexible DOM traversal
- **Trafilatura**: Fast content extraction, optimized for articles
- **Future parsers**: lxml, html5lib, domain-specific parsers

Key requirements:
1. **Extensibility**: Easy to add new parsers without modifying existing code
2. **Flexibility**: Choose optimal parser for specific content types
3. **Reliability**: Automatic fallback if primary parser fails
4. **Maintainability**: Clear separation of concerns
5. **Performance**: Optimal parser selection based on content characteristics

A naive approach using conditional logic would violate Open/Closed Principle and become unmanageable as more parsers are added.

## Decision
Implement **Strategy Pattern** for parser selection and execution:

### Core Components

**IParser Interface (Abstract Strategy):**
```python
class IParser(ABC):
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

**Concrete Strategies:**
- `BeautifulSoupParser` - General purpose, comprehensive parsing
- `TrafilaturaParser` - Content-focused, fast article extraction
- Future parsers can implement the same interface

**ParserService (Context):**
```python
class ParserService:
    def __init__(
        self,
        primary_parser: IParser,
        fallback_parser: Optional[IParser] = None,
        enable_fallback: bool = True
    ):
        self.primary_parser = primary_parser
        self.fallback_parser = fallback_parser
        self.enable_fallback = enable_fallback

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        """Execute parsing strategy with fallback."""
        # Strategy selection and execution logic
```

### Strategy Selection Algorithm
```python
def recommend_parser(
    url: Optional[str] = None,
    content_type: Optional[str] = None
) -> str:
    """
    Recommend optimal parser based on content analysis.

    Selection Rules:
    1. Explicit content type → specific parser
    2. URL pattern analysis → likely content type
    3. Default fallback → safe general parser
    """
    if content_type == "article":
        return "trafilatura"
    if url and "news" in url:
        return "trafilatura"
    return "beautifulsoup"
```

## Consequences

### Positive
- **Open/Closed Principle**: New parsers can be added without modifying existing code
- **Dependency Inversion**: High-level modules depend on abstractions, not implementations
- **Testability**: Each parser can be tested independently
- **Flexibility**: Runtime parser selection based on content characteristics
- **Maintainability**: Clear separation of parsing strategies
- **Extensibility**: Easy to add domain-specific parsers for specialized content

### Negative
- **Complexity**: Additional abstraction layer increases complexity
- **Overhead**: Strategy selection adds minimal performance overhead
- **Testing**: Need to test multiple parser implementations
- **Interface Rigidity**: All parsers must implement the same interface

### Risks
- Interface bloat as common patterns are added
- Inconsistent parser behavior across implementations
- Performance overhead of abstraction
- Incorrect parser selection for edge cases

### Mitigations
- Keep interface focused and cohesive (Interface Segregation Principle)
- Comprehensive test suite validates parser equivalence
- Performance metrics guide optimization
- Clear documentation of parser characteristics and use cases

## Implementation Details

### Parser Runtime Selection
```python
def parse(
    self,
    html: str,
    url: Optional[str] = None,
    parser_type: Optional[str] = None
) -> ParserResult:
    """
    Parse HTML with strategy selection.

    Selection Priority:
    1. Explicit parser_type parameter
    2. Automatic recommendation based on content analysis
    3. Default primary parser
    """
    if parser_type == "beautifulsoup":
        parser = self._get_parser("beautifulsoup")
    elif parser_type == "trafilatura":
        parser = self._get_parser("trafilatura")
    else:
        # Automatic selection
        recommended = self.recommend_parser(url)
        parser = self._get_parser(recommended)

    return parser.parse(html, url)
```

### Fallback Strategy Execution
```python
def parse_with_fallback(
    self,
    html: str,
    url: Optional[str] = None
) -> ParserResult:
    """
    Execute parsing with fallback strategy.

    Fallback Rules:
    1. Try primary parser
    2. If fails and fallback enabled, try fallback parser
    3. If both fail, raise ParserError with details
    """
    try:
        return self.primary_parser.parse(html, url)
    except ParserError as primary_error:
        if not self.enable_fallback or not self.fallback_parser:
            raise ParserError(
                f"Primary parser failed: {primary_error}"
            ) from primary_error

        try:
            return self.fallback_parser.parse(html, url)
        except ParserError as fallback_error:
            raise ParserError(
                f"All parsers failed. Primary: {primary_error}, "
                f"Fallback: {fallback_error}"
            ) from fallback_error
```

### Metrics Collection
```python
def track_parser_performance(self, parser: IParser, duration: float):
    """Track parser performance metrics."""
    self.parser_usage[parser.__class__.__name__] += 1
    self.total_parse_time += duration
    self.successful_parses += 1
```

## Future Extensions

### Custom Parser Registration
```python
def register_parser(self, parser_type: str, parser: IParser):
    """Register custom parser for specific use cases."""
    self.available_parsers[parser_type] = parser
```

### Parser Chaining
```python
class ChainedParser(IParser):
    """Chain multiple parsers for specialized processing."""
    def __init__(self, parsers: List[IParser]):
        self.parsers = parsers

    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        """Execute parsers in sequence, combining results."""
        base_result = self.parsers[0].parse(html, url)
        # Enhance with subsequent parsers
        for parser in self.parsers[1:]:
            enhancement = parser.parse(html, url)
            # Combine results
        return base_result
```

### Parser Configuration Profiles
```python
class ParserProfile:
    """Configuration profile for specific use cases."""
    def __init__(
        self,
        primary_parser: IParser,
        fallback_parser: Optional[IParser],
        selection_rules: Dict[str, str]
    ):
        self.primary_parser = primary_parser
        self.fallback_parser = fallback_parser
        self.selection_rules = selection_rules
```

## References
- Gang of Four Design Patterns: Strategy Pattern
- IParser Interface: `backend/core/interfaces/parser.py`
- ParserService: `backend/parser/parser_service.py`
- Existing Implementations: `backend/parser/implementations/`

## Related Decisions
- ADR-0004: Use BeautifulSoup4 and Trafilatura as Dual Parser Strategy
- ADR-0006: Clean Architecture for Parser Module

## Implementation Status
✅ Implemented in Milestone 4
- IParser Interface: Defined and stable
- ParserService: Strategy selection and execution
- BeautifulSoupParser: General purpose strategy
- TrafilaturaParser: Content-focused strategy
- Fallback mechanism: Automatic failure recovery
- Performance metrics: Parser usage tracking

## Examples

### Basic Strategy Usage
```python
# Automatic strategy selection
service = ParserService(
    primary_parser=BeautifulSoupParser(),
    fallback_parser=TrafilaturaParser()
)

result = service.parse(html, url="https://news.example.com/article")
# Automatically selects Trafilatura for news content
```

### Explicit Strategy Selection
```python
# Force specific parser
result = service.parse(
    html,
    url="https://example.com",
    parser_type="beautifulsoup"
)
```

### Custom Strategy
```python
class ECommerceParser(IParser):
    """Custom strategy for e-commerce content."""
    def parse(self, html: str, url: Optional[str] = None) -> ParserResult:
        # E-commerce specific parsing logic
        pass

# Use custom strategy
service = ParserService(
    primary_parser=ECommerceParser(),
    fallback_parser=BeautifulSoupParser()
)
```