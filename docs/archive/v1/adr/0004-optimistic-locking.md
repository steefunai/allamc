# ADR-0004 — Optimistic locking via conditional update (SQLAlchemy version_id_col)
Status: Accepted

## Context
Dispatchers, technicians (offline) and accountants edit the same rows. The previous build learned that a
version column alone does not protect a plain save if the ORM is not told to use it.

## Decision
Versioned tables map `version` with `version_id_col`, so every ORM UPDATE is
`UPDATE … WHERE id = :id AND version = :v` and zero rows raises `StaleDataError` → 409
`VERSION_CONFLICT`. Clients always send the version they read. Bulk `update()` statements on versioned
tables must include the version predicate (verify.sh flags them for review).

**Exception:** `number_series` uses a pessimistic `SELECT … FOR UPDATE` inside the issuing transaction,
because gapless numbering requires serialising issuers rather than failing them.

## Consequences
- Offline sync turns 409s into conflict-queue entries rather than silent overwrites (ADR-0006).
- Tests must include a concurrent-write failure path for every versioned entity a slice touches.
