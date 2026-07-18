# ADR-0001

# Use FastAPI

Status

Accepted

---

## Context

The project requires a high-performance asynchronous REST API for AI workloads.

The framework should support:

- Async programming
- OpenAPI
- Type hints
- Automatic validation
- Dependency Injection

---

## Alternatives

- Django
- Flask
- Quart

---

## Decision

Use FastAPI.

---

## Reason

FastAPI provides:

- Excellent async support
- Automatic Swagger
- Automatic validation
- Strong typing
- Production readiness

---

## Consequences

Pros

- High performance
- Easy API documentation
- Modern Python ecosystem

Cons

- Smaller ecosystem than Django