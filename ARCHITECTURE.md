# ARCHITECTURE.md

# AI Website Intelligence Platform

---

# Vision

Convert any website into structured business intelligence.

---

# High-Level Pipeline

Website URL

↓

Validation

↓

Crawler

↓

HTML Parser

↓

Content Cleaner

↓

Structured Extraction

↓

Technology Detection

↓

LLM

↓

Business Intelligence

↓

Structured JSON

---

# Folder Structure

backend/

    api/

    config/

    core/

    crawler/

    parser/

    cleaner/

    extractor/

    technology/

    llm/

    nlp/

    services/

    database/

    models/

    storage/

    workers/

    utils/

tests/

docs/

docker/

scripts/

.github/

---

# Module Responsibilities

## crawler/

Responsible for

- Playwright
- Crawl4AI
- Downloading pages
- Retry logic
- Robots.txt
- Rate limiting

---

## parser/

Responsible for

- BeautifulSoup
- HTML parsing
- DOM extraction

---

## cleaner/

Responsible for

- Removing boilerplate
- Cleaning HTML
- Markdown conversion
- Readability optimization

---

## extractor/

Responsible for

Extracting

- Metadata
- Contacts
- Social Links
- Company Details
- Internal Links
- External Links

---

## technology/

Responsible for

Technology fingerprinting

Examples

React

Angular

Vue

WordPress

Cloudflare

Google Analytics

Tailwind

Bootstrap

Next.js

Node.js

Laravel

Django

FastAPI

---

## llm/

Responsible for

Prompt engineering

Business summary

Keyword extraction

Industry detection

Company profile generation

Future RAG support

---

## database/

Responsible for

SQLAlchemy

Alembic

Repositories

Persistence

---

## api/

Responsible for

REST API

Swagger

Validation

Error handling

Response models

---

# Data Flow

URL

↓

Crawler

↓

HTML

↓

Parser

↓

Clean Text

↓

Extractor

↓

Technology Detector

↓

LLM

↓

JSON

↓

Database

---

# Initial API

POST /analyze

Body

{
"url":"https://example.com"
}

Returns

{
"title":"",
"company_name":"",
"summary":"",
"emails":[],
"phones":[],
"addresses":[],
"technologies":[],
"keywords":[],
"social_links":{},
"processing_time":"",
"status":"success"
}

---

# Design Principles

Keep modules independent.

Avoid circular dependencies.

Prefer composition over inheritance.

Prefer interfaces over concrete implementations.

Prefer dependency injection.

Every module should have a single responsibility.

---

# Future Expansion

The architecture should support

Vector Databases

Knowledge Graphs

Multi-Agent Systems

RAG

Batch Crawling

Queue Workers

Kafka

Redis

Enterprise Scaling

without major refactoring.