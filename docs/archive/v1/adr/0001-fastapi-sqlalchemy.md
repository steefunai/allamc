# ADR-0001 — FastAPI + SQLAlchemy 2.0 + Alembic for the backend
Status: Accepted · Decision ref: D-70

## Context
The owner chose Python. Candidates: Django (+DRF/Ninja) or FastAPI + SQLAlchemy. The codebase is built
largely by AI agents under strict boundary rules (modular monolith, ports, co-transactional audit).

## Decision
FastAPI for HTTP and OpenAPI generation, SQLAlchemy 2.0 (typed ORM, explicit `Session` = the unit of
work passed to `AuditPort.append(entry, session)`), Alembic for forward-only migrations, Pydantic v2 for
schemas, uv for packaging.

## Consequences
- No built-in admin, auth or migrations generator conventions: auth is a planned module (VS-001) and the
  staff console is part of the React app.
- Explicit sessions make transaction boundaries visible, which suits the audit and locking invariants.
- OpenAPI is first-class; the frontend client is generated from it.
