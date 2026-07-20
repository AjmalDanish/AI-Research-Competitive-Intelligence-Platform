# Content Processor - Sequence Diagrams

## Overview

This document provides sequence diagrams showing the interaction flow between components in the Content Processor architecture.

## Main Processing Flow

### **Diagram: Complete Processing Pipeline**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ProcessingService
    participant WS as WhitespaceNormalizer
    participant UN as UnicodeNormalizer
    participant HE as HTMLEntityDecoder
    participant BR as BoilerplateRemover
    participant NR as NavigationRemover
    participant DD as DuplicateDetector
    participant PR as ParagraphReconstructor
    participant HA as HeadingAssociator
    participant RO as ReadingOrderReconstructor
    participant MC as MetadataCleaner
    participant CV as ContentValidator
    participant RESULT as ProcessingResult

    Client->>PS: process(content, metadata, source_url)
    activate PS

    PS->>PS: initialize_processing_context()

    PS->>WS: process(content, metadata, options, context)
    activate WS
    WS->>WS: _normalize_linebreaks(content)
    WS->>WS: _collapse_multiple_spaces(content)
    WS->>WS: _trim_whitespace(content)
    WS->>PS: normalized_content, updated_metadata
    deactivate WS

    PS->>UN: process(normalized_content, updated_metadata, options, context)
    activate UN
    UN->>UN: unicodedata.normalize(content, unicode_form)
    UN->>UN: _normalize_quotes(content)
    UN->>UN: _normalize_dashes(content)
    UN->>UN: _remove_invisible_characters(content)
    UN->>PS: unicode_normalized_content, updated_metadata
    deactivate UN

    PS->>HE: process(unicode_normalized_content, updated_metadata, options, context)
    activate HE
    HE->>HE: html.unescape(content)
    HE->>HE: _handle_remaining_entities(content)
    HE->>PS: decoded_content, updated_metadata
    deactivate HE

    PS->>BR: process(decoded_content, updated_metadata, options, context)
    activate BR
    BR->>BR: _remove_comments(content)
    BR->>BR: _remove_advertisements(content)
    BR->>BR: _remove_social_media(content)
    BR->>BR: _remove_boilerplate_patterns(content)
    BR->>PS: cleaned_content, updated_metadata
    deactivate BR

    PS->>NR: process(cleaned_content, updated_metadata, options, context)
    activate NR
    NR->>NR: _remove_navigation(content)
    NR->>NR: _remove_footers(content)
    NR->>NR: _remove_sidebars(content)
    NR->>PS: cleaned_content, updated_metadata
    deactivate NR

    PS->>DD: process(cleaned_content, updated_metadata, options, context)
    activate DD
    DD->>DD: _split_into_paragraphs(content)
    DD->>DD: _detect_duplicates(paragraphs, options)
    DD->>DD: _remove_duplicates(paragraphs, duplicates)
    DD->>PS: deduplicated_content, updated_metadata
    deactivate DD

    PS->>PR: process(deduplicated_content, updated_metadata, options, context)
    activate PR
    PR->>PR: _split_into_paragraphs(content)
    PR->>PR: _normalize_paragraphs(paragraphs, options)
    PR->>PR: _merge_short_paragraphs(paragraphs, options)
    PR->>PR: _split_long_paragraphs(paragraphs, options)
    PR->>PS: reconstructed_content, updated_metadata
    deactivate PR

    PS->>HA: process(reconstructed_content, updated_metadata, options, context)
    activate HA
    HA->>HA: _extract_headings(content)
    HA->>HA: _associate_content_with_headings(content, headings, options)
    PS->>PS: content_with_headings, updated_metadata
    deactivate HA

    PS->>RO: process(content_with_headings, updated_metadata, options, context)
    activate RO
    RO->>RO: _reorder_by_html_structure(content_sections)
    RO->>RO: _reorder_by_visual_order(content)
    PS->PS: reordered_content, updated_metadata
    deactivate RO

    PS->>MC: process(reordered_content, updated_metadata, options, context)
    activate MC
    MC->>MC: _clean_metadata_fields(metadata)
    MC->>MC: _remove_duplicate_metadata(metadata)
    MC->>MC: _validate_metadata(metadata)
    PS->PS: content, cleaned_metadata
    deactivate MC

    PS->>CV: process(content, cleaned_metadata, options, context)
    activate CV
    CV->>CV: _validate_content_length(content, options)
    CV->>CV: _validate_non_empty(content, options)
    CV->CV: _validate_content_quality(content, options)
    CV->>CV: _validate_content_structure(content, options)
    CV->CV: _validate_content_consistency(content, metadata)
    PS->>PS: content, validated_metadata
    deactivate CV

    PS->>RESULT: ProcessingResult(source_url, content, metadata, metrics)
    activate RESULT
    RESULT->>RESULT: normalized_text.calculate_statistics()
    RESULT->>RESULT: content_sections, text_segments, metadata
    RESULT->>RESULT: calculate_quality_score()
    RESULT-->>Client: ProcessingResult
    deactivate RESULT

    deactivate PS
```

### **Flow Description:**

1. **Client Request**: Client calls `ProcessingService.process()` with content
2. **Initialization**: Service initializes processing context and metrics
3. **Sequential Processing**: Each processor executes in pipeline order:
   - **Stage 1-3**: Normalization (whitespace, unicode, HTML entities)
   - **Stage 4-5**: Cleanup (boilerplate, navigation/footer)
   - **Stage 6-7**: Structure (duplicate detection, paragraph reconstruction)
   - **Stage 8-9**: Organization (heading association, reading order)
   - **Stage 10-11**: Finalization (metadata cleanup, validation)
4. **Result Assembly**: Service creates `ProcessingResult` with all processed data
5. **Metrics Collection**: Each stage contributes to overall metrics
6. **Quality Scoring**: Final quality and determinism scores calculated

---

## Processor Registration Flow

### **Diagram: Processor Registration**

```mermaid
sequenceDiagram
    actor Client as Developer
    participant PS as ProcessingService
    participant REGISTRY as Processor Registry
    participant WS as WhitespaceNormalizer
    participant CUSTOM as CustomProcessor

    Client->>PS: ProcessingService(options=ProcessingOptions())
    activate PS

    PS->>REGISTRY: _register_default_processors()
    activate REGISTRY
    REGISTRY->>WS: WhitespaceNormalizer()
    REGISTRY->>REGISTRY: processors[WHITESPACE_NORMALIZATION] = WS
    REGISTRY-->>PS: default_processors_registered
    deactivate REGISTRY

    Client->>CUSTOM: class CustomProcessor(IParser)
    activate CUSTOM
    CUSTOM->>CUSTOM: implement IContentProcessor methods
    CUSTOM-->>Client: CustomProcessor implementation
    deactivate CUSTOM

    Client->>PS: register_processor(CustomProcessor())
    PS->>PS: processors[CUSTOM_STAGE] = CustomProcessor()
    PS->>PS: available_stages.append(CUSTOM_STAGE)

    Client->>PS: get_available_stages()
    PS-->>Client: [WHITESPACE_NORMALIZATION, ..., CUSTOM_STAGE]

    deactivate PS
```

### **Flow Description:**

1. **Service Initialization**: Default processors are registered
2. **Custom Implementation**: Developer creates custom processor
3. **Registration**: Custom processor registered in service
4. **Pipeline Extension**: Custom processor becomes part of pipeline
5. **Validation**: All stages available for processing

---

## Stage-Level Processing Flow

### **Diagram: Individual Processor Execution**

```mermaid
sequenceDiagram
    actor PS as ProcessingService
    participant PROC as Processor Implementation
    participant VALIDATOR as Validation
    participant METRICS as Metrics Collection
    participant ERRORS as Error Handling

    PS->>PROC: process(content, metadata, options, context)
    activate PROC

    PROC->>PROC: is_enabled(options) = is_processor_enabled
    alt Processor Enabled
        PROC->>PROC: should_skip_content(content, options)

        alt Content Should be Skipped
            PROC->>PROC: return content, metadata
        else Content Should be Processed
            PROC->>VALIDATOR: validate(content, metadata, options)
            activate VALIDATOR
            VALIDATOR->>VALIDATOR: check_content_constraints(content, options)
            VALIDATOR->>VALIDATOR: check_configuration_options(options)
            VALIDATOR->>VALIDATOR: check_dependencies(options)
            VALIDATOR-->>PROC: validation_errors
            deactivate VALIDATOR

            alt Validation Passed
                PROC->>PROC: start_timer()
                PROC->>PROC: execute_processing_logic(content)
                PROC->>PROC: stop_timer()

                PROC->>PROC: create_stage_result(success=True, duration)
                PROC->>PROC: update_context_metrics(context)

                PROC-->>PS: processed_content, updated_metadata
            else Validation Failed
                alt Strict Validation
                    PROC->>ERRORS: raise ProcessingValidationError(validation_errors)
                else Lenient Validation
                    PROC->>PROC: log_validation_warnings(validation_errors)
                    PROC->>PROC: create_stage_result(success=True, warnings=validation_errors)
                    PROC-->>PS: processed_content, updated_metadata
                end
            end
        end
    else Processor Disabled
        PROC->>PROC: return content, metadata
    end

    deactivate PROC
```

### **Flow Description:**

1. **Enablement Check**: Processor checks if enabled in options
2. **Skip Check**: Short-circuit for empty or too-large content
3. **Pre-Validation**: Validate content and configuration
4. **Execution**: Execute processing logic with timing
5. **Result Creation**: Create stage result with metrics
6. **Error Handling**: Handle validation errors based on strictness
7. **Context Updates**: Update processing context and metrics

---

## Error Handling Flow

### **Diagram: Error Handling and Recovery**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ProcessingService
    participant PROC1 as Primary Processor
    participant PROC2 as Secondary Processor
    participant LOG as Error Logger
    participant METRICS as Metrics Collection

    Client->>PS: process(content, metadata, source_url)
    activate PS

    PS->>PS: initialize_processing_context()
    PS->>PS: initialize_metrics()

    loop For each processing stage
        PS->>PROC1: process(current_content, metadata, options, context)

        alt Processing Succeeds
            PROC1-->>PS: processed_content, updated_metadata
            PS->>PS: update_context_with_success()
        else Processing Fails
            PROC1-->>PS: ProcessorError
            PS->>LOG: log_error(primary_processor, error, stage)

            PS->>METRICS: increment_failed_processing_count()
            PS->>PS: update_processing_metrics()

            alt Error is Critical (Validation Failure)
                PS->>PS: handle_critical_error(error, stage)
                PS->>CLIENT: raise ProcessingValidationError(validation_errors)
            else Error is Recoverable (Processing Failure)
                PS->>PS: log_recovery_attempt(stage)
                PS->>PS: continue_to_next_stage()
            end
        end
    end

    PS->>PS: finalize_processing_result()
    PS->>PS: calculate_quality_scores()
    PS->PS: increment_successful_processing_count()

    PS-->>CLIENT: ProcessingResult

    deactivate PS
```

### **Flow Description:**

1. **Processing Attempt**: Try primary processor first
2. **Success Path**: Update metrics and continue to next stage
3. **Failure Path**: Log error and determine criticality
4. **Critical Errors**: Validation failures stop processing
5. **Recoverable Errors**: Processing failures allow continuation
6. **Metrics Collection**: Track success/failure rates
7. **Result Finalization**: Create final result with quality scores

---

## Metrics Collection Flow

### **Diagram: Processing Metrics Collection**

```mermaid
sequenceDiagram
    participant CLIENT as Client Code
    participant PS as ProcessingService
    participant PROC as Processor Implementation
    participant METRICS as ProcessingMetrics
    participant COUNTERS as Metrics Counters

    CLIENT->>PS: process(content, metadata, source_url)
    activate PS

    PS->>COUNTERS: increment_total_processing_count()
    PS->>PS: start_overall_timer()

    loop For each processing stage
        PS->>PROC: process(current_content, metadata, options, context)
        activate PROC

        PROC->>PROC: start_timer()
        PROC->>PROC: execute_processing_logic(current_content)
        PROC->PROC: stop_timer()

        PROC->>PROC: calculate_stage_metrics(input_len, output_len, duration)
        PROC->>PROC: update_internal_metrics()

        PROC-->>PS: processed_content, updated_metadata, stage_metrics
        deactivate PROC

        PS->>METRICS: add_stage_result(stage_result)
        PS->>COUNTERS: update_parser_usage(stage)
        PS->>PS: update_performance_counters()

        alt Processing Succeeded
            PS->>COUNTERS: increment_successful_processing_count()
        else Processing Failed
            PS->COUNTERS: increment_failed_processing_count()
        end
    end

    PS->>PS: stop_overall_timer()

    PS->>METRICS: calculate_compression_ratio(input_len, output_len)
    PS->>METRICS: calculate_overall_duration()
    PS->PS: calculate_success_rate()
    PS->METRICS: finalize_metrics()

    PS-->>CLIENT: ProcessingResult with complete metrics

    deactivate PS
```

### **Flow Description:**

1. **Counter Initialization**: Increment total processing counter
2. **Timing**: Start overall processing timer
3. **Stage Processing**: Execute each stage with timing
4. **Stage Metrics**: Collect per-stage metrics
5. **Aggregation**: Aggregate metrics across all stages
6. **Counters**: Update success/failure counters
7. **Finalization**: Calculate overall metrics and ratios
8. **Result Creation**: Include complete metrics in final result

---

## Content Validation Flow

### **Diagram: Content Validation Process**

```mermaid
sequenceDiagram
    participant CV as ContentValidator
    participant LENGTH as Length Validator
    participant EMPTY as Empty Content Validator
    participant QUALITY as Quality Validator
    participant STRUCTURE as Structure Validator
    participant CONSISTENCY as Consistency Validator
    participant METADATA as Metadata Validator

    CV->>LENGTH: validate_content_length(content, options)
    activate LENGTH

    alt Content Length Valid
        LENGTH-->>CV: length_valid=True
    else Content Length Invalid
        LENGTH-->>CV: length_valid=False, error="Content too short"
    end

    deactivate LENGTH

    CV->>EMPTY: validate_non_empty(content, options)
    activate EMPTY

    alt Empty Content Allowed
        EMPTY->>EMPTY: check_if_empty()
        alt Content is Empty
            EMPTY-->>CV: empty_allowed=True, warning="Content is empty"
        else Content Not Empty
            EMPTY-->>CV: empty_allowed=False
        end
    else Empty Content Not Allowed
        EMPTY->>EMPTY: check_if_empty()
        alt Content is Empty
            EMPTY-->>CV: empty_allowed=False, error="Content is empty"
        else Content Not Empty
            EMPTY-->>CV: empty_allowed=True
        end
    end

    deactivate EMPTY

    CV->>QUALITY: validate_content_quality(content, options)
    activate QUALITY

    QUALITY->>QUALITY: check_excessive_whitespace(content)
    QUALITY->>QUALITY: check_consecutive_linebreaks(content)
    QUALITY->>QUALITY: check_very_short_content(content)
    QUALITY-->>CV: quality_issues_found

    deactivate QUALITY

    CV->>STRUCTURE: validate_content_structure(content, options)
    activate STRUCTURE

    STRUCTURE->>STRUCTURE: check_balanced_quotes(content)
    STRUCTURE->>STRUCTURE: check_unusual_patterns(content)
    STRUCTURE-->>CV: structure_issues_found

    deactivate STRUCTURE

    CV->>CONSISTENCY: validate_content_consistency(content, metadata)
    activate CONSISTENCY

    CONSISTENCY->>CONSISTENCY: check_title_in_content(content, metadata)
    CONSISTENCY->>CONSISTENCY: check_language_validity(metadata)
    CONSISTENCY-->>CV: consistency_issues_found

    deactivate CONSISTENCY

    CV->>CV: compile_validation_errors(length_errors, empty_errors, quality_errors, structure_errors, consistency_errors)

    alt Strict Validation and Errors Found
        CV->>CV: validation_passed=False
        CV->>CV: raise ProcessingValidationError(all_errors)
    else Lenient Validation or No Errors
        CV->>CV: validation_passed=(len(all_errors) == 0)
        CV->>CV: validation_warnings=errors_with_lower_severity
    end
```

### **Flow Description:**

1. **Length Validation**: Check if content meets minimum length requirements
2. **Empty Content Validation**: Check if content is empty and if that's allowed
3. **Quality Validation**: Check for quality issues (whitespace, patterns)
4. **Structure Validation**: Check for structural issues (quotes, patterns)
5. **Consistency Validation**: Check content-metadata consistency
6. **Error Compilation**: Compile all validation errors and warnings
7. **Decision**: Based on strict validation settings, raise error or add warnings
8. **Result Update**: Update validation status in metadata

---

## Duplicate Detection Flow

### **Diagram: Duplicate Detection Process**

```mermaid
sequenceDiagram
    participant DD as DuplicateDetector
    participant SPLIT as Content Splitter
    participant COMP as Sequence Matcher
    participant METRICS as Metrics Collector

    DD->>SPLIT: split_into_paragraphs(content)
    activate SPLIT
    SPLIT->>SPLIT: detect_paragraph_boundaries(content)
    SPLIT->>SPLIT: extract_paragraphs(content)
    SPLIT-->>DD: paragraphs
    deactivate SPLIT

    DD->>DD: initialize_duplicate_tracking()
    DD->>DD: duplicate_count = 0

    loop For each paragraph i in paragraphs
        DD->>DD: check_minimum_length(paragraph[i], options)

        alt Paragraph Long Enough
            loop For each paragraph j in paragraphs[i+1:]
                DD->>DD: check_minimum_length(paragraph[j], options)

                alt Both Paragraphs Long Enough
                    DD->>COMP: calculate_similarity(paragraph[i], paragraph[j])
                    activate COMP
                    COMP->>COMP: SequenceMatcher(None, paragraph[i], paragraph[j]).ratio()
                    COMP-->>DD: similarity_score
                    deactivate COMP

                    alt Exact Match
                        DD->>DD: add_duplicate(i, j)
                        DD->>DD: increment_duplicate_count()
                    else Near-Duplicate Check
                        alt Similarity Threshold Exceeded
                            DD->>DD: add_duplicate(i, j)
                            DD->DD: increment_duplicate_count()
                        end
                    end
                end
            end
    end

    DD->>DD: collect_duplicate_indices(duplicates)
    DD->>DD: create_unique_paragraphs(paragraphs, duplicates)
    DD->>DD: reconstruct_content(unique_paragraphs)

    DD->>METRICS: update_metrics(duplicate_count, input_length, output_length)

    DD-->>DD: deduplicated_content, updated_metadata
```

### **Flow Description:**

1. **Content Splitting**: Split content into paragraphs
2. **Duplicate Tracking**: Initialize duplicate counter
3. **Pairwise Comparison**: Compare all paragraph pairs
4. **Similarity Calculation**: Use SequenceMatcher for near-duplicate detection
5. **Duplicate Detection**: Identify duplicates exceeding threshold
6. **Content Reconstruction**: Remove duplicates keeping first occurrence
7. **Metrics Update**: Track duplicate count and content reduction

---

## Paragraph Reconstruction Flow

### **Diagram: Paragraph Reconstruction Process**

```mermaid
sequenceDiagram
    participant PR as ParagraphReconstructor
    participant SPLIT as Paragraph Splitter
    participant FILTER as Paragraph Filter
    participant MERGE as Paragraph Merger
    participant SPLIT_LONG as Long Paragraph Splitter
    participant METRICS as Metrics Collector

    PR->>SPLIT: split_into_paragraphs(content)
    activate SPLIT
    SPLIT->>SPLIT: detect_paragraph_boundaries(content)
    SPLIT->>SPLIT: clean_paragraph_lines(content)
    SPLIT-->>PR: raw_paragraphs
    deactivate SPLIT

    PR->>FILTER: normalize_paragraphs(raw_paragraphs, options)
    activate FILTER

    loop For each paragraph in raw_paragraphs
        FILTER->>FILTER: check_min_length(paragraph, options)
        FILTER->>FILTER: check_max_length(paragraph, options)
        FILTER->>FILTER: is_meaningful_content(paragraph, options)

        alt Paragraph Meets All Criteria
            FILTER->>FILTER: add_to_normalized(paragraph)
        else Paragraph Fails Criteria
            FILTER->>FILTER: add_to_filtered(paragraph)
        end
    end

    FILTER-->>PR: normalized_paragraphs
    deactivate FILTER

    PR->>MERGE: merge_short_paragraphs(normalized_paragraphs, options)
    activate MERGE

    loop For each paragraph in normalized_paragraphs
        MERGE->>MERGE: check_if_short(paragraph, options)

        alt Paragraph is Short and Has Next Paragraph
            MERGE->>MERGE: merge_with_next_paragraph(paragraph, next_paragraph)
            MERGE->>MERGE: create_merged_paragraph(paragraph, next_paragraph)
            MERGE->>MERGE: increment_merge_count()
        else Paragraph is Normal Length or No Next Paragraph
            MERGE->>MERGE: keep_as_is(paragraph)
        end
    end

    MERGE-->>PR: merged_paragraphs
    deactivate MERGE

    PR->>SPLIT_LONG: split_long_paragraphs(merged_paragraphs, options)
    activate SPLIT_LONG

    loop For each paragraph in merged_paragraphs
        SPLIT_LONG->>SPLIT_LONG: check_if_long(paragraph, options)

        alt Paragraph is Too Long
            SPLIT_LONG->>SPLIT_LONG: split_by_sentences(paragraph)
            SPLIT_LONG->SPLIT_LONG: reassemble_short_chunks(sentences)
            SPLIT_LONG->>SPLIT_LONG: ensure_chunk_size_limits(sentences, options)
            SPLIT_LONG->>SPLIT_LONG: create_short_paragraphs(sentences)
        else Paragraph Length is Normal
            SPLIT_LONG->>SPLIT_LONG: keep_as_is(paragraph)
        end
    end

    SPLIT_LONG-->>PR: finalized_paragraphs
    deactivate SPLIT_LONG

    PR->>PR: reconstruct_content(finalized_paragraphs)
    PR->>METRICS: update_metrics(original_len, final_len, processing_time)

    PR-->>PR: reconstructed_content
```

### **Flow Description:**

1. **Paragraph Splitting**: Split content into paragraph units
2. **Normalization**: Filter paragraphs by length and quality criteria
3. **Short Paragraph Merging**: Merge adjacent short paragraphs
4. **Long Paragraph Splitting**: Split long paragraphs by sentences
5. **Content Reconstruction**: Reassemble normalized paragraphs
6. **Metrics Update**: Track paragraph count and content statistics

---

## Heading Association Flow

### **Diagram: Heading Association Process**

```mermaid
sequenceDiagram
    participant HA as HeadingAssociator
    participant EXTRACT as Heading Extractor
    participant ASSOCIATOR as Content-Heading Mapper
    participant STRUCTURE as Structure Builder

    HA->>EXTRACT: extract_headings(content)
    activate EXTRACT
    EXTRACT->>EXTRACT: find_heading_markers(content, "#")
    EXTRACT->>EXTRACT: extract_heading_level(marker)
    EXTRACT->>EXTRACT: extract_heading_text(content, marker)
    EXTRACT->>EXTRACT: determine_line_number(content, marker)
    EXTRACT->>EXTRACT: create_heading_object(level, text, line_number)

    loop For each heading found
        EXTRACT->>EXTRACT: add_to_heading_list(heading)
    end

    EXTRACT-->>HA: headings_with_levels
    deactivate EXTRACT

    HA->>ASSOCIATOR: associate_content_with_headings(content, headings, options)
    activate ASSOCIATOR

    ASSOCIATOR->>ASSOCIATOR: split_content_by_lines(content)
    ASSOCIATOR->>ASSOCIATOR: initialize_content_mapping(current_section=None, current_content=[])

    loop For each line in content_lines
        ASSOCIATOR->>ASSOCIATOR: check_if_line_is_heading(line, headings)

        alt Line is Heading
            ASSOCIATOR->>ASSOCIATOR: finalize_current_section(current_section, current_content)
            ASSOCIATOR->>ASSOCIATOR: create_new_section(heading, current_section=heading)
            ASSOCIATOR->>ASSOCIATOR: reset_content_tracking()
        else Line is Content
            ASSOCIATOR->>ASSOCIATOR: append_to_current_content(line)
            ASSOCIATOR->>ASSOCIATOR: increment_section_length()
        end
    end

    ASSOCIATOR->>ASSOCIATOR: finalize_last_section(current_section, current_content)
    ASSOCIATOR->>ASSOCIATOR: create_content_sections_list(all_sections)

    ASSOCIATOR-->>HA: content_sections
    deactivate ASSOCIATOR

    HA->>STRUCTURE: build_section_hierarchy(content_sections, headings)
    activate STRUCTURE

    STRUCTURE->>STRUCTURE: establish_parent_child_relationships(sections)
    STRUCTURE->>STRUCTURE: validate_section_hierarchy(sections)

    STRUCTURE->>STRUCTURE: calculate_section_depths(sections)
    STRUCTURE->>STRUCTURE: create_section_tree_structure(sections)

    STRUCTURE-->>HA: structured_content_sections
    deactivate STRUCTURE

    HA-->>HA: content_sections_with_hierarchy
```

### **Flow Description:**

1. **Heading Extraction**: Find all headings with levels and positions
2. **Content Association**: Map content lines to nearest heading
3. **Section Creation**: Create sections for each heading with associated content
4. **Hierarchy Building**: Establish parent-child relationships between sections
5. **Structure Validation**: Ensure proper heading hierarchy (h1 before h2, etc.)
6. **Final Output**: Content sections with hierarchical structure

---

## Integration with Parser Module Flow

### **Diagram: Parser → Processor Integration**

```mermaid
sequenceDiagram
    actor Client as Client Code
    participant PS as ParserService
    participant CS as CrawlerService
    participant PROC as ProcessingService
    participant RESULT as ProcessingResult

    Client->>PS: parse(html, url)
    activate PS
    PS->>PS: recommend_parser(url, content_type)
    PS->>PS: execute_parser(html, url)
    PS-->>Client: ParserResult(html, metadata, metrics)
    deactivate PS

    Client->>PROC: process(parser_result.text_content, parser_result.metadata.__dict__, parser_result.url)
    activate PROC

    PROC->>PROC: validate_and_normalize_content(parser_result.text_content, parser_result.metadata)
    PROC->>PROC: execute_processing_pipeline(parser_result.text_content)
    PROC->>PROC: extract_content_structure(parser_result.text_content)
    PROC->>PROC: normalize_and_clean_content(parser_result.text_content)
    PROC->>PROC: remove_boilerplate_and_duplicates(parser_result.text_content)
    PROC->>PROC: reconstruct_paragraphs(parser_result.text_content)
    PROC->PROC: organize_content_structure(parser_result.text_content)
    PROC->>PROC: validate_processed_content(parser_result.text_content)

    PROC->>RESULT: ProcessingResult(source_url=parser_result.url, ...)
    PROC->>RESULT: add_content_quality_score()
    PROC->>PROC: add_determinism_score()

    PROC-->>Client: ProcessingResult
    deactivate PROC

    Client->>RESULT: access_processed_content()
    Client->>RESULT: get_effective_content()
    Client->>RESULT: get_reading_order_text()
```

### **Flow Description:**

1. **Parser Execution**: Parse HTML into structured content
2. **Content Validation**: Validate and normalize parsed content
3. **Pipeline Execution**: Execute all 11 processing stages
4. **Content Structure**: Extract and organize content structure
5. **Quality Enhancement**: Remove boilerplate, duplicates, normalize
6. **Organization**: Reconstruct paragraphs, headings, reading order
7. **Validation**: Final quality and consistency checks
8. **Result Creation**: Create comprehensive processing result
9. **Quality Scoring**: Calculate content quality and determinism scores
10. **Access Methods**: Provide methods to access processed content

---

## Summary

These sequence diagrams illustrate the complete flow of operations within the Content Processor architecture:

- **Main Processing Flow**: Complete pipeline with all 11 stages
- **Processor Registration**: Dynamic processor registration and validation
- **Stage-Level Processing**: Detailed individual processor execution with validation
- **Error Handling**: Robust error handling and recovery mechanisms
- **Metrics Collection**: Performance tracking and analysis
- **Content Validation**: Comprehensive validation process
- **Duplicate Detection**: Detailed duplicate detection algorithm
- **Paragraph Reconstruction**: Paragraph normalization process
- **Heading Association**: Content-to-heading mapping and structure building
- **Parser Integration**: Integration with parser module for end-to-end processing

These diagrams provide developers with a clear understanding of how components interact and data flows through the content processing system.