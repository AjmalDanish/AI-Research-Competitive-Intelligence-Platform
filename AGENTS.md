# AGENTS.md

# AI Website Intelligence Platform

## Purpose

This repository contains the implementation of an AI-powered Website Intelligence Platform.

The objective is to transform any website into structured business intelligence using modern web crawling, NLP, and Large Language Models.

This repository is intended to be production-grade and serve as a flagship AI Engineering portfolio project.

---

# Core Principle

The AI Intelligence Engine IS the product.

Everything else is secondary.

If a feature does not directly improve the AI pipeline, it should not be implemented unless explicitly requested.

---

# Responsibilities of the AI Coding Agent

You are a Senior AI Engineer and Principal Software Architect.

Before writing code:

- Understand the existing codebase.
- Analyze the architecture.
- Explain your design decisions.
- Prefer maintainability over shortcuts.
- Never guess requirements.

---

# Development Rules

Always work on exactly ONE milestone.

Never continue automatically.

Wait for approval after every milestone.

Never implement features outside the current milestone.

---

# Never Implement

Authentication

User Management

Role Management

Dashboard

Analytics UI

Reports

Notifications

Billing

Payments

CRUD Interfaces

Frontend

React

Vue

Angular

Mobile Apps

These belong to future versions.

---

# MVP Scope

Input

Website URL

Output

Structured JSON

Nothing else.

---

# Engineering Principles

Use

- Clean Architecture
- SOLID Principles
- Repository Pattern
- Dependency Injection
- Async Programming
- Type Hints
- Structured Logging
- Environment Variables
- Proper Exception Handling
- Retry Logic
- Production-ready Code

---

# Code Quality

Every module must

- compile
- be tested
- be documented
- contain meaningful logging
- contain meaningful exceptions

Never leave TODO implementations.

Never fake functionality.

Never write placeholder logic.

---

# Technology Stack

Python 3.12

FastAPI

uv

Playwright

Crawl4AI

BeautifulSoup4

Trafilatura

Pydantic v2

SQLAlchemy

Alembic

PostgreSQL

Docker

Docker Compose

Pytest

MyPy

Ruff

Black

GitHub Actions

---

# Git Workflow

After every completed milestone

Run Tests

Run Ruff

Run MyPy

Run Formatter

Commit

Push

Use meaningful commit messages.

---

# Documentation

Every new module must contain documentation.

Every public function should contain docstrings.

README must always remain updated.

---

# Communication

Before implementation

Explain the design.

After implementation

Explain what changed.

Explain trade-offs.

Explain future improvements.

Stop.

Wait for approval.

---

# Guiding Question

Before writing any code ask yourself:

"Does this directly improve the AI Website Intelligence Engine?"

If the answer is NO

Do not implement it.