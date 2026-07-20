# Parser Module - Sequence Diagrams

## Overview

This document provides sequence diagrams showing the interaction flow between components in the Parser Foundation architecture.

## Main Parsing Flow

### **Diagram: Single Document Parsing**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ParserService
    participant BSOUP as BeautifulSoupParser
    participant TRAF as TrafilaturaParser
    participant RESULT as ParserResult

    Client->>PS: parse(html, url)
    activate PS

    PS->>PS: recommend_parser(url, content_type)
    PS-->>PS: selected_parser = "beautifulsoup"

    alt Primary Parser Success
        PS->>BSOUP: parse(html, url)
        activate BSOUP

        BSOUP->>BSOUP: extract_title(html)
        BSOUP->>BSOUP: extract_text_content(html)
        BSOUP->>BSOUP: detect_language(html)
        BSOUP->>BSOUP: extract_metadata(html)
        BSOUP->>BSOUP: extract_headings(html)
        BSOUP->>BSOUP: extract_links(html, url)
        BSOUP->>BSOUP: extract_images(html)
        BSOUP->>BSOUP: extract_scripts(html)
        BSOUP->>BSOUP: extract_stylesheets(html)
        BSOUP->>BSOUP: create_parsing_metrics()

        BSOUP-->>PS: ParserResult
        deactivate BSOUP

        PS-->>Client: ParserResult
        deactivate PS

    else Primary Parser Failure
        PS->>BSOUP: parse(html, url)
        activate BSOUP
        BSOUP-->>PS: ParserError
        deactivate BSOUP

        alt Fallback Enabled
            PS->>TRAF: parse(html, url)
            activate TRAF

            TRAF->>TRAF: extract_title(html)
            TRAF->>TRAF: extract_text_content(html)
            TRAF->>TRAF: detect_language(html)
            TRAF->>TRAF: extract_metadata(html)
            TRAF->>TRAF: extract_headings(html)
            TRAF->>TRAF: create_parsing_metrics()

            TRAF-->>PS: ParserResult
            deactivate TRAF

            PS-->>Client: ParserResult
            deactivate PS
        else Fallback Disabled
            PS-->>Client: ParserError
            deactivate PS
        end
    end
```

### **Flow Description:**

1. **Client Request**: Client code calls `ParserService.parse()` with HTML content and optional URL
2. **Parser Selection**: Service analyzes URL/content and selects appropriate parser
3. **Primary Parsing**: Primary parser executes all extraction methods
4. **Success Path**: If primary succeeds, `ParserResult` is returned to client
5. **Fallback Path**: If primary fails and fallback is enabled, secondary parser attempts parsing
6. **Error Handling**: If all parsers fail or fallback is disabled, error is returned to client

---

## Crawler Integration Flow

### **Diagram: Crawler → Parser Integration**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant CS as CrawlerService
    participant PS as ParserService
    participant PARSER as Parser Implementation
    participant RESULT as ParserResult

    Client->>CS: crawl(url)
    activate CS

    CS->>CS: validate_url(url)
    CS->>CS: check_robots_txt(url)
    CS->>CS: fetch_html(url)
    CS-->>Client: CrawlResult(html, url, metrics)

    deactivate CS

    Client->>PS: parse(crawl_result.html, crawl_result.url)
    activate PS

    PS->>PS: recommend_parser(crawl_result.url)
    PS->>PARSER: parse(crawl_result.html, crawl_result.url)
    activate PARSER

    PARSER->>PARSER: extract_title(html)
    PARSER->>PARSER: extract_text_content(html)
    PARSER->>PARSER: extract_metadata(html)
    PARSER->>PARSER: extract_headings(html)
    PARSER->>PARSER: extract_links(html, url)
    PARSER->>PARSER: extract_images(html)
    PARSER->>PARSER: extract_scripts(html)
    PARSER->>PARSER: extract_stylesheets(html)
    PARSER->>PARSER: create_parsing_metrics()

    PARSER-->>PS: ParserResult
    deactivate PARSER

    PS-->>Client: ParserResult
    deactivate PS

    Client->>RESULT: access parsed content
    activate RESULT
    RESULT-->>Client: title, content, metadata, etc.
    deactivate RESULT
```

### **Flow Description:**

1. **Crawling Phase**:
   - Client requests URL crawling
   - CrawlerService validates URL, checks robots.txt, fetches HTML
   - Returns `CrawlResult` with HTML and metadata

2. **Parsing Phase**:
   - Client passes crawled HTML to ParserService
   - ParserService selects appropriate parser
   - Parser extracts all structured content
   - Returns `ParserResult` with comprehensive data

3. **Data Access**:
   - Client accesses parsed content through `ParserResult` properties
   - Can query specific content (links, images, headings, etc.)

---

## Batch Processing Flow

### **Diagram: Batch Document Parsing**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ParserService
    participant PARSER as Parser Implementation
    participant METRICS as ParsingMetrics

    Client->>PS: parse_batch(html_list, show_progress=True)
    activate PS

    loop For each HTML document
        PS->>PS: recommend_parser(url)
        PS->>PARSER: parse(html, url)
        activate PARSER

        PARSER->>PARSER: extract_title(html)
        PARSER->>PARSER: extract_text_content(html)
        PARSER->>PARSER: extract_metadata(html)
        PARSER->>PARSER: extract_headings(html)
        PARSER->>PARSER: extract_links(html, url)
        PARSER->>PARSER: extract_images(html)
        PARSER->>PARSER: extract_scripts(html)
        PARSER->>PARSER: extract_stylesheets(html)
        PARSER->>PARSER: create_parsing_metrics()

        PARSER-->>PS: ParserResult
        deactivate PARSER

        PS->>METRICS: update_metrics()
        PS->>Client: progress_update(index, total) if show_progress
    end

    PS-->>Client: List[ParserResult]
    deactivate PS
```

### **Flow Description:**

1. **Batch Request**: Client provides list of HTML documents
2. **Iterative Processing**: Service processes each document sequentially
3. **Progress Updates**: Optional progress reporting during processing
4. **Metrics Collection**: Each parse updates service-level metrics
5. **Result Return**: Returns list of `ParserResult` objects in same order as input

---

## Parser Selection Strategy Flow

### **Diagram: Parser Recommendation Logic**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ParserService
    participant ANALYZER as URLAnalyzer
    participant SELECTOR as ParserSelector

    Client->>PS: recommend_parser(url, content_type)
    activate PS

    par URL Analysis
        PS->>ANALYZER: analyze_url(url)
        activate ANALYZER
        ANALYZER->>ANALYZER: extract_domain(url)
        ANALYZER->>ANALYZER: detect_content_type(url)
        ANALYZER->>ANALYZER: classify_url_pattern(url)
        ANALYZER-->>PS: url_analysis
        deactivate ANALYZER
    and Content Type Analysis
        PS->>SELECTOR: analyze_content_type(content_type)
        activate SELECTOR
        SELECTOR->>SELECTOR: map_content_to_parser(content_type)
        SELECTOR-->>PS: content_recommendation
        deactivate SELECTOR
    end

    PS->>PS: combine_recommendations(url_analysis, content_recommendation)
    PS-->>Client: "beautifulsoup" | "trafilatura"
    deactivate PS
```

### **Flow Description:**

1. **URL Analysis**: Analyzes URL domain, path patterns, and indicators
2. **Content Type Analysis**: Maps explicit content types to parser capabilities
3. **Recommendation Combining**: Combines analyses into final recommendation
4. **Parser Selection**: Returns recommended parser type

---

## Error Handling Flow

### **Diagram: Error Handling and Fallback**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ParserService
    participant PRIMARY as Primary Parser
    participant FALLBACK as Fallback Parser
    participant LOGGER as ErrorLogger

    Client->>PS: parse(html, url)
    activate PS

    PS->>PRIMARY: parse(html, url)
    activate PRIMARY

    alt Primary Parser Success
        PRIMARY-->>PS: ParserResult
        deactivate PRIMARY
        PS->>LOGGER: log_success(parser_used, metrics)
        PS-->>Client: ParserResult
    else Primary Parser Failure
        PRIMARY-->>PS: ParserError
        deactivate PRIMARY
        PS->>LOGGER: log_error(primary_parser, error)

        alt Fallback Enabled
            PS->>FALLBACK: parse(html, url)
            activate FALLBACK

            alt Fallback Parser Success
                FALLBACK-->>PS: ParserResult
                deactivate FALLBACK
                PS->>LOGGER: log_fallback_success(fallback_parser, metrics)
                PS-->>Client: ParserResult
            else Fallback Parser Failure
                FALLBACK-->>PS: ParserError
                deactivate FALLBACK
                PS->>LOGGER: log_complete_failure(primary_parser, fallback_parser)
                PS-->>Client: ParserError
            end
        else Fallback Disabled
            PS-->>Client: ParserError
        end
    end

    deactivate PS
```

### **Flow Description:**

1. **Primary Attempt**: Try primary parser first
2. **Success Path**: Log success and return result
3. **Failure Path**: Log error and attempt fallback if enabled
4. **Fallback Success**: Log fallback success and return result
5. **Complete Failure**: Log complete failure and return error
6. **No Fallback**: Return error immediately if fallback disabled

---

## Metrics Collection Flow

### **Diagram: Parsing Metrics Collection**

```mermaid
sequenceDiagram
    participant CLIENT as Client Code
    participant PS as ParserService
    participant PARSER as Parser Implementation
    participant METRICS as ParsingMetrics
    participant COUNTERS as MetricsCounters

    CLIENT->>PS: parse(html, url)
    activate PS

    note over PS,COUNTERS: Metrics Collection Process

    PS->>COUNTERS: increment_total_parses()
    PS->>PS: start_timer()

    PS->>PARSER: parse(html, url)
    activate PARSER

    PARSER->>PARSER: extract_content(html)
    PARSER->>PARSER: track_internal_metrics()
    PARSER-->>PS: ParserResult with metrics
    deactivate PARSER

    PS->>PS: stop_timer()
    PS->>PS: calculate_parse_duration()

    alt Parse Success
        PS->>COUNTERS: increment_successful_parses()
        PS->>METRICS: update_average_parse_time(duration)
        PS->>COUNTERS: update_parser_usage(parser_type)
    else Parse Failure
        PS->>COUNTERS: increment_failed_parses()
    end

    PS-->>CLIENT: ParserResult
    deactivate PS

    CLIENT->>PS: get_metrics()
    activate PS
    PS->>COUNTERS: get_all_metrics()
    PS-->>CLIENT: metrics_dict
    deactivate PS
```

### **Flow Description:**

1. **Parse Initialization**: Increment total parse counter and start timer
2. **Parser Execution**: Parser executes and tracks internal metrics
3. **Parse Completion**: Stop timer and calculate duration
4. **Success Metrics**: Update success counters and average times
5. **Failure Metrics**: Update failure counters
6. **Metrics Retrieval**: Client can query metrics at any time

---

## Content Extraction Flow

### **Diagram: Detailed Content Extraction**

```mermaid
sequenceDiagram
    participant PS as ParserService
    participant PARSER as Parser Implementation
    participant DOM as DOM Parser
    participant EXTRACTOR as Content Extractor
    participant METADATA as Metadata Extractor
    participant CLEANER as Text Cleaner

    PS->>PARSER: parse(html, url)
    activate PARSER

    PARSER->>DOM: parse_html(html)
    activate DOM
    DOM-->>PARSER: DOM Tree
    deactivate DOM

    par Parallel Content Extraction
        PARSER->>METADATA: extract_metadata(DOM)
        activate METADATA
        METADATA->>METADATA: extract_title()
        METADATA->>METADATA: extract_description()
        METADATA->>METADATA: extract_keywords()
        METADATA->>METADATA: extract_open_graph()
        METADATA->>METADATA: extract_twitter_cards()
        METADATA-->>PARSER: MetaData
        deactivate METADATA

        and
        PARSER->>EXTRACTOR: extract_headings(DOM)
        activate EXTRACTOR
        EXTRACTOR->>EXTRACTOR: traverse_heading_elements()
        EXTRACTOR->>EXTRACTOR: extract_heading_properties()
        EXTRACTOR-->>PARSER: List[Heading]
        deactivate EXTRACTOR

        and
        PARSER->>EXTRACTOR: extract_links(DOM, url)
        activate EXTRACTOR
        EXTRACTOR->>EXTRACTOR: find_link_elements()
        EXTRACTOR->>EXTRACTOR: classify_links_internal_external()
        EXTRACTOR-->>PARSER: List[Link]
        deactivate EXTRACTOR

        and
        PARSER->>EXTRACTOR: extract_images(DOM)
        activate EXTRACTOR
        EXTRACTOR->>EXTRACTOR: find_image_elements()
        EXTRACTOR->>EXTRACTOR: extract_image_dimensions()
        EXTRACTOR-->>PARSER: List[Image]
        deactivate EXTRACTOR
    end

    PARSER->>CLEANER: clean_text_content(DOM)
    activate CLEANER
    CLEANER->>CLEANER: remove_html_tags()
    CLEANER->>CLEANER: normalize_whitespace()
    CLEANER->>CLEANER: remove_special_characters()
    CLEANER-->>PARSER: cleaned_text
    deactivate CLEANER

    PARSER->>PARSER: create_parsing_metrics()
    PARSER->>PARSER: assemble_parser_result()

    PARSER-->>PS: ParserResult
    deactivate PARSER
```

### **Flow Description:**

1. **DOM Parsing**: HTML is parsed into DOM tree
2. **Parallel Extraction**: Multiple extractions occur in parallel:
   - Metadata extraction (title, description, Open Graph, etc.)
   - Heading extraction (h1-h6 hierarchy)
   - Link extraction (with internal/external classification)
   - Image extraction (with dimensions)
3. **Text Cleaning**: Text content is cleaned and normalized
4. **Result Assembly**: All components combined into `ParserResult`

---

## Link Classification Flow

### **Diagram: Internal/External Link Classification**

```mermaid
sequenceDiagram
    participant PARSER as Parser Implementation
    participant CLASSIFIER as LinkClassifier
    participant URLUTILS as URL Utilities

    PARSER->>CLASSIFIER: classify_links(links, base_url)
    activate CLASSIFIER

    loop For each link
        CLASSIFIER->>URLUTILS: parse_url(link.url)
        activate URLUTILS
        URLUTILS-->>CLASSIFIER: parsed_url
        deactivate URLUTILS

        CLASSIFIER->>URLUTILS: parse_url(base_url)
        activate URLUTILS
        URLUTILS-->>CLASSIFIER: base_parsed_url
        deactivate URLUTILS

        alt Same Domain
            CLASSIFIER->>CLASSIFIER: compare_domains(parsed_url, base_parsed_url)
            CLASSIFIER->>CLASSIFIER: link.is_external = False
        else Different Domain
            CLASSIFIER->>CLASSIFIER: link.is_external = True
        end

        alt NoFollow Attribute
            CLASSIFIER->>CLASSIFIER: check_nofollow_attribute()
            CLASSIFIER->>CLASSIFIER: link.is_nofollow = True
        else Followable
            CLASSIFIER->>CLASSIFIER: link.is_nofollow = False
        end
    end

    CLASSIFIER-->>PARSER: classified_links
    deactivate CLASSIFIER
```

### **Flow Description:**

1. **URL Parsing**: Both link URL and base URL are parsed
2. **Domain Comparison**: Domains are compared to determine internal/external
3. **NoFollow Check**: HTML attributes are checked for nofollow directive
4. **Classification**: Each link is marked as internal/external and nofollow/followable

---

## Language Detection Flow

### **Diagram: Content Language Detection**

```mermaid
sequenceDiagram
    participant PARSER as Parser Implementation
    participant HTML as HTML Analyzer
    participant DETECTOR as Language Detector

    PARSER->>HTML: analyze_html(html)
    activate HTML

    alt HTML Language Attribute
        HTML->>HTML: extract_lang_attribute()
        HTML-->>PARSER: language_from_html
    else No HTML Language Attribute
        HTML->>DETECTOR: detect_language_from_content(text_content)
        activate DETECTOR

        DETECTOR->>DETECTOR: analyze_character_patterns()
        DETECTOR->>DETECTOR: check_stop_words()
        DETECTOR->>DETECTOR: apply_nlp_models()

        DETECTOR-->>HTML: detected_language
        deactivate DETECTOR

        HTML-->>PARSER: detected_language
    end

    deactivate HTML

    PARSER->>PARSER: update_metadata_language(language)
```

### **Flow Description:**

1. **HTML Analysis**: Check for HTML lang attribute first
2. **Language Detection**: If no HTML language, use content analysis
3. **NLP Methods**: Apply character patterns, stop words, and ML models
4. **Language Update**: Update metadata with detected language

---

## Custom Parser Integration Flow

### **Diagram: Adding New Parser Implementation**

```mermaid
sequenceDiagram
    participant DEV as Developer
    participant IPARSER as IParser Interface
    participant CUSTOM as CustomParser
    participant SERVICE as ParserService
    participant REGISTRY as Parser Registry

    DEV->>IPARSER: implement IParser interface
    activate IPARSER

    DEV->>CUSTOM: class CustomParser(IParser):
    activate CUSTOM

    CUSTOM->>CUSTOM: def parse(html, url) -> ParserResult
    CUSTOM->>CUSTOM: def extract_title(html) -> Optional[str]
    CUSTOM->>CUSTOM: def extract_text_content(html) -> str
    CUSTOM->>CUSTOM: def detect_language(html) -> Optional[str]
    CUSTOM->>CUSTOM: def extract_metadata(html) -> MetaData

    CUSTOM-->>DEV: CustomParser implementation
    deactivate CUSTOM
    deactivate IPARSER

    DEV->>REGISTRY: register_parser("custom", CustomParser)
    activate REGISTRY
    REGISTRY->>REGISTRY: add_to_available_parsers("custom")
    REGISTRY-->>DEV: registration_success
    deactivate REGISTRY

    DEV->>SERVICE: ParserService(primary_parser=CustomParser())
    activate SERVICE
    SERVICE-->>DEV: configured_service
    deactivate SERVICE

    DEV->>SERVICE: service.parse(html, url)
    activate SERVICE
    SERVICE->>CUSTOM: parse(html, url)
    activate CUSTOM
    CUSTOM-->>SERVICE: ParserResult
    deactivate CUSTOM
    SERVICE-->>DEV: ParserResult
    deactivate SERVICE
```

### **Flow Description:**

1. **Interface Implementation**: Developer creates class implementing `IParser`
2. **Method Implementation**: All abstract methods are implemented
3. **Parser Registration**: New parser is registered in system
4. **Service Configuration**: Service is configured with custom parser
5. **Normal Usage**: Custom parser works like built-in parsers

---

## Performance Optimization Flow

### **Diagram: Performance Metrics and Optimization**

```mermaid
sequenceDiagram
    participant CLIENT as Client Code
    participant SERVICE as ParserService
    participant METRICS as Metrics Analyzer
    participant OPTIMIZER as Performance Optimizer

    loop Multiple Parse Operations
        CLIENT->>SERVICE: parse(html, url)
        activate SERVICE
        SERVICE-->>CLIENT: ParserResult
        deactivate SERVICE
    end

    CLIENT->>SERVICE: get_metrics()
    activate SERVICE
    SERVICE-->>CLIENT: performance_data
    deactivate SERVICE

    CLIENT->>METRICS: analyze_performance(performance_data)
    activate METRICS

    METRICS->>METRICS: calculate_success_rate()
    METRICS->>METRICS: identify_slow_operations()
    METRICS->>METRICS: compare_parser_performance()
    METRICS->>METRICS: detect_memory_patterns()

    METRICS-->>CLIENT: performance_analysis
    deactivate METRICS

    alt Performance Issues Detected
        CLIENT->>OPTIMIZER: optimize_configuration(performance_analysis)
        activate OPTIMIZER

        OPTIMIZER->>OPTIMIZER: adjust_parser_selection()
        OPTIMIZER->>OPTIMIZER: update_timeout_settings()
        OPTIMIZER->>OPTIMIZER: configure_batch_sizes()
        OPTIMIZER->>OPTIMIZER: enable_caching_strategies()

        OPTIMIZER-->>CLIENT: optimization_recommendations
        deactivate OPTIMIZER
    end
```

### **Flow Description:**

1. **Normal Operation**: Service processes parse requests
2. **Metrics Collection**: Client collects performance metrics
3. **Performance Analysis**: Metrics are analyzed for patterns
4. **Optimization**: Recommendations made for configuration improvements

---

## Summary

These sequence diagrams illustrate the complete flow of operations within the Parser Foundation architecture:

- **Main Parsing Flow**: Core parsing operation with fallback
- **Crawler Integration**: How parser works with crawler module
- **Batch Processing**: Handling multiple documents efficiently
- **Parser Selection**: How appropriate parser is chosen
- **Error Handling**: Robust error handling and fallback mechanisms
- **Metrics Collection**: Performance tracking and analysis
- **Content Extraction**: Detailed content extraction process
- **Link Classification**: Internal/external link determination
- **Language Detection**: Content language identification
- **Custom Integration**: Adding new parser implementations
- **Performance Optimization**: Metrics-based optimization

These diagrams provide developers with a clear understanding of how components interact and data flows through the system.