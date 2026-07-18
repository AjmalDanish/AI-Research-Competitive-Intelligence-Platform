# ADR-0002

# Use PostgreSQL

Status

Accepted

---

## Context

The project stores structured website intelligence.

SQLite is insufficient for future scaling.

---

## Alternatives

SQLite

MongoDB

MySQL

---

## Decision

Use PostgreSQL from day one.

---

## Reason

Supports

- JSONB
- Full-text search
- Extensions
- High scalability

---

## Consequences

Pros

Production ready

Easy migrations

Reliable

Cons

Requires Docker during development