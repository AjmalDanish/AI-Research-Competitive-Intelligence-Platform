# ADR-0004: Use BeautifulSoup4 and Trafilatura as Dual Parser Strategy

## Status
Accepted

## Context
Milestone 4 required implementing a robust HTML parsing foundation for the AI Website Intelligence Platform. The platform needed to handle various types of web content including:

- General websites with rich metadata
- News articles and blog posts
- E-commerce product pages
- Documentation sites
- Marketing pages

Single parser solutions presented limitations:
- BeautifulSoup4: Powerful but slow, requires more configuration for content-focused extraction
- Trafilatura: Fast content extraction but limited metadata support
- lxml: Performance-focused but lenient parsing could introduce issues
- html5lib: Very lenient but slow

## Decision
Implement a **dual parser strategy** using both BeautifulSoup4 and Trafilatura:

**BeautifulSoup4 as Primary Parser:**
- Comprehensive metadata extraction (Open Graph, Twitter Cards)
- Full DOM traversal and CSS selector support
- Flexible element selection and filtering
- Well-documented and stable API
- Extensive community support

**Trafilatura as Secondary/Fallback Parser:**
- Optimized for news/article content
- Fast text extraction and cleaning
- Built-in language detection
- Automatic content formatting
- Robust handling of malformed HTML

**ParserService Orchestration:**
- Automatic parser selection based on content analysis
- Configurable fallback mechanisms
- Performance metrics tracking
- Strategy pattern for extensibility

## Consequences

### Positive
- **Versatility**: Handles diverse content types effectively
- **Reliability**: Fallback ensures parsing always succeeds
- **Performance**: Parser selection optimizes for content type
- **Extensibility**: Strategy pattern allows easy addition of new parsers
- **Quality**: Both parsers are well-maintained and production-ready
- **Flexibility**: Different content types can use optimal parsing strategies

### Negative
- **Complexity**: Maintaining two parsers increases system complexity
- **Dependencies**: Additional dependency requirements
- **Memory**: Both parser libraries must be loaded
- **Testing**: Increased test coverage requirements for multiple parsers
- **Configuration**: Need to manage multiple parser configurations

### Risks
- Parser inconsistency between the two implementations
- Different behavior for same content type
- Maintenance burden of keeping both parsers updated
- Potential performance overhead of dual implementation

### Mitigations
- Standardized `IParser` interface ensures consistent output
- Comprehensive test suite validates parser equivalence
- Performance metrics guide parser selection optimization
- Clear documentation of each parser's strengths/weaknesses
- Regular dependency updates and security scanning

## Alternatives Considered

### Alternative 1: BeautifulSoup4 Only
**Pros:**
- Single dependency
- Comprehensive feature set
- Well-established

**Cons:**
- Slower performance for large documents
- Requires more configuration for content extraction
- Less optimized for article content

**Rejected:** Performance limitations for content-focused use cases

### Alternative 2: Trafilatura Only
**Pros:**
- Fast performance
- Excellent content extraction
- Built-in language detection

**Cons:**
- Limited metadata support
- Less flexible for general HTML
- Fewer customization options

**Rejected:** Insufficient metadata capabilities for comprehensive analysis

### Alternative 3: lxml Only
**Pros:**
- Very fast performance
- XPath support

**Cons:**
- Less intuitive API
- More lenient parsing
- Limited content extraction features

**Rejected:** Less suitable for diverse content types and metadata needs

### Alternative 4: Dynamic Parser Selection from Multiple Libraries
**Pros:**
- Maximum flexibility
- Optimal parser for each scenario

**Cons:**
- Excessive complexity
- High maintenance burden
- Inconsistent behaviors

**Rejected:** Over-engineering for MVP requirements

## Implementation Details

### Parser Selection Strategy
```python
def recommend_parser(url: Optional[str], content_type: Optional[str]) -> str:
    """
    Recommend parser based on content analysis.

    Rules:
    - News/article content → Trafilatura (fast, optimized)
    - General websites → BeautifulSoup4 (comprehensive)
    - Unknown content → BeautifulSoup4 (safe default)
    """
    if content_type and "article" in content_type:
        return "trafilatura"
    if url and any(domain in url for domain in NEWS_DOMAINS):
        return "trafilatura"
    return "beautifulsoup"
```

### Fallback Mechanism
```python
def parse(html: str, url: Optional[str] = None) -> ParserResult:
    """
    Parse with automatic fallback.

    Process:
    1. Try primary parser
    2. If fails and fallback enabled, try secondary parser
    3. If both fail, raise ParserError
    """
    try:
        return self.primary_parser.parse(html, url)
    except ParserError:
        if self.fallback_parser and self.enable_fallback:
            return self.fallback_parser.parse(html, url)
        raise
```

## References
- BeautifulSoup4 Documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Trafilatura Documentation: https://trafilatura.readthedocs.io/
- IParser Interface: `backend/core/interfaces/parser.py`
- ParserService: `backend/parser/parser_service.py`

## Related Decisions
- ADR-0001: Use FastAPI
- ADR-0002: Use PostgreSQL
- ADR-0003: Use Playwright
- ADR-0005: Strategy Pattern for Parser Selection

## Implementation Status
✅ Implemented in Milestone 4
- BeautifulSoupParser: `backend/parser/implementations/beautifulsoup_parser.py`
- TrafilaturaParser: `backend/parser/implementations/trafilatura_parser.py`
- ParserService: `backend/parser/parser_service.py`
- IParser Interface: `backend/core/interfaces/parser.py`