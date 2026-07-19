# Dependency Reintroduction Plan

## Current Status: Milestone 3 Complete ✅
**Active Dependencies:** Pydantic, HTTPX, AIOFiles, Development Tools  
**Removed Dependencies:** ML/AI libraries, legacy scraping, optional features  
**Core Functionality:** ✅ Working with zero broken imports  

---

## Dependency Reintroduction by Milestone

### 🎯 Milestone 4: Parser Foundation (Next)

#### Dependencies to Add:
```toml
[tool.poetry.dependencies]
beautifulsoup4 = "^4.12.0"
trafilatura = "^1.6.0"
lxml = "^5.0.0"  # Required by BeautifulSoup4
```

#### Commands:
```bash
poetry add beautifulsoup4 trafilatura lxml
```

#### Justification:
- **BeautifulSoup4**: HTML parsing and DOM traversal
- **Trafilatura**: Content extraction and text cleaning  
- **lxml**: High-performance XML/HTML parser (required by BS4)

#### Files to Implement:
- `backend/parser/html_parser.py` - HTML parsing with BeautifulSoup4
- `backend/parser/content_extractor.py` - Content extraction with Trafilatura
- `backend/parser/text_cleaner.py` - Text cleaning and normalization

#### Impact on Code:
- Extend `CrawlerResult` with parsed content
- Add `IParser` interface (polymorphism with `ICrawler`)
- Create parser implementations
- Add parsing tests

---

### 🎯 Milestone 5: Data Processing

#### Dependencies to Add:
```toml
[tool.poetry.dependencies]
pandas = "^2.1.4"
numpy = "^1.26.3"
```

#### Commands:
```bash
poetry add pandas numpy
```

#### Justification:
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing and array operations
- Enable advanced data transformations and analytics

#### Files to Enable:
- `backend/app/services/data_pipeline.py` (currently commented)
- Data transformation and aggregation
- Batch processing capabilities

#### Impact on Code:
- Enable data pipeline processing
- Add analytics to crawler results
- Support data export formats (CSV, JSON, Excel)

#### Test Files to Re-enable:
- `tests/test_data_pipeline.py`

---

### 🎯 Milestone 6: ML Integration

#### Dependencies to Add:
```toml
[tool.poetry.dependencies]
scikit-learn = "^1.4.0"
```

#### Commands:
```bash
poetry add scikit-learn
```

#### Justification:
- **scikit-learn**: Machine learning algorithms
- Enable pattern recognition, clustering, classification
- Support predictive analytics

#### Files to Enable:
- `backend/app/services/analytics_service.py` (currently commented)
- ML-powered content analysis
- Pattern recognition in crawl results

#### Impact on Code:
- Add ML features to analytics service
- Enable competitor similarity analysis
- Support predictive market intelligence

#### Test Files to Re-enable:
- Test cases for analytics service
- ML model validation tests

---

### 🎯 Milestone 7: LLM Integration

#### Dependencies to Add:
```toml
[tool.poetry.dependencies]
openai = "^1.10.0"
langchain = "^0.1.4"
transformers = "^4.36.2"
torch = "^2.1.2"  # Required by transformers
tiktoken = "^0.5.0"  # OpenAI tokenization
```

#### Commands:
```bash
poetry add openai langchain transformers torch tiktoken
```

#### Justification:
- **openai**: GPT models for advanced text analysis
- **langchain**: LLM application framework
- **transformers**: Hugging Face models
- **torch**: PyTorch backend for transformers
- **tiktoken**: Efficient tokenization for OpenAI models

#### Files to Implement:
- `backend/llm/openai_client.py` - OpenAI API integration
- `backend/llm/analysis_engine.py` - LLM-powered content analysis
- `backend/llm/summarization.py` - Automated summarization
- `backend/llm/classification.py` - Content classification

#### Impact on Code:
- Add LLM-powered content understanding
- Enable intelligent summarization
- Support semantic search and classification
- Add competitor comparison features

---

### 🎯 Milestone 8: Production Features (Optional)

#### Dependencies to Add:
```toml
[tool.poetry.dependencies]
redis = "^5.0.1"
slowapi = "^0.5.0"
celery = "^5.3.6"
```

#### Commands:
```bash
poetry add redis slowapi celery
```

#### Justification:
- **redis**: High-performance caching and session storage
- **slowapi**: Rate limiting for API protection
- **celery**: Distributed task queue for background processing

#### Files to Enable:
- `backend/app/core/rate_limiting.py` (currently commented)
- Caching middleware
- Background task processing
- Distributed crawler orchestration

#### Impact on Code:
- Add rate limiting to API endpoints
- Implement result caching
- Enable distributed crawling
- Add background job processing

#### Test Files to Re-enable:
- `tests/test_security.py`

---

## Dependency Management Strategy

### 1. Milestone-Based Approach
- Only add dependencies required for current milestone
- Keep environment minimal and focused
- Clear dependency documentation per milestone

### 2. Virtual Environment Strategy
- Use Poetry for dependency management
- Maintain lock files for reproducibility
- Document installation commands

### 3. Testing Strategy
- Test core functionality with minimal dependencies
- Add dependency-specific tests when reintroduced
- Maintain test coverage across dependency changes

### 4. Documentation Strategy
- Update `requirements.txt` with milestone comments
- Maintain `pyproject.toml` with version constraints
- Document dependency rationale

---

## Installation Commands Reference

### Current Milestone 3 Environment
```bash
# Install current dependencies
poetry install

# Verify installation
poetry show
```

### Adding Milestone 4 Dependencies
```bash
# Add parsing dependencies
poetry add beautifulsoup4 trafilatura lxml

# Update lock file
poetry lock

# Verify new dependencies
poetry show | grep -E "beautifulsoup4|trafilatura|lxml"
```

### Adding Future Milestone Dependencies
```bash
# Milestone 5 - Data Processing
poetry add pandas numpy

# Milestone 6 - ML Integration
poetry add scikit-learn

# Milestone 7 - LLM Integration
poetry add openai langchain transformers torch tiktoken

# Milestone 8 - Production Features
poetry add redis slowapi celery
```

---

## Troubleshooting Guide

### Issue: Build Failures on Windows
**Problem:** Some packages require C compilation  
**Solution:** Use pre-built wheels or conda packages

```bash
# Use conda for problematic packages
conda install pandas numpy scikit-learn

# Or use Poetry with pre-built wheels
poetry add pandas --prefer-binary
```

### Issue: Version Conflicts
**Problem:** Dependency version conflicts  
**Solution:** Use Poetry's resolver

```bash
# Update lock file with resolver
poetry lock --no-update

# Check dependency tree
poetry show --tree
```

### Issue: Missing Test Dependencies
**Problem:** Tests fail due to missing optional packages  
**Solution:** Add test dependencies separately

```bash
# Add development dependencies
poetry add --group dev pytest-cov pytest-mock

# Add milestone-specific test dependencies
poetry add --group dev pandas numpy  # When testing Milestone 5+
```

---

## Environment Size Comparison

### Current Environment (Milestone 3)
- **Dependencies:** 10 core packages
- **Install Size:** ~50MB
- **Startup Time:** <1 second
- **Complexity:** Low

### Full Environment (All Milestones)
- **Dependencies:** 30+ packages
- **Install Size:** ~2GB+ 
- **Startup Time:** 3-5 seconds
- **Complexity:** High

### Benefits of Milestone-Based Approach
- **Faster development** - Minimal environment
- **Faster testing** - Reduced dependency overhead
- **Clear dependencies** - Easier troubleshooting
- **Better isolation** - Milestone-specific issues

---

## Migration Checklists

### Milestone 4 Readiness ✅
- [x] Current environment stable
- [x] No broken imports in core code
- [x] Documentation updated
- [ ] Add BeautifulSoup4, Trafilatura, lxml
- [ ] Implement parser interfaces
- [ ] Add parser tests
- [ ] Update documentation

### Milestone 5 Readiness
- [ ] Add pandas, numpy
- [ ] Enable data pipeline service
- [ ] Add data transformation tests
- [ ] Update analytics documentation
- [ ] Performance testing

### Milestone 6 Readiness  
- [ ] Add scikit-learn
- [ ] Enable analytics service
- [ ] Add ML model tests
- [ ] Validate ML performance
- [ ] Update ML documentation

### Milestone 7 Readiness
- [ ] Add OpenAI, LangChain, Transformers
- [ ] Implement LLM services
- [ ] Add LLM integration tests
- [ ] Validate LLM performance
- [ ] Update AI documentation

### Milestone 8 Readiness
- [ ] Add Redis, SlowAPI, Celery
- [ ] Enable rate limiting
- [ ] Add caching layer
- [ ] Implement distributed crawling
- [ ] Production deployment testing

---

## Summary

The dependency simplification was **successful and strategic**. Each removed package has a clear reintroduction plan tied to specific future milestones. This approach provides:

✅ **Minimal Complexity** - Current environment focused and clean  
✅ **Clear Roadmap** - Each milestone has defined dependencies  
✅ **Flexible Development** - Easy to add features as needed  
✅ **Risk Mitigation** - Dependencies added only when required  
✅ **Performance Optimization** - Minimal overhead for current scope  

**Next Step:** Proceed with Milestone 4 using the clean, focused environment established in this milestone.