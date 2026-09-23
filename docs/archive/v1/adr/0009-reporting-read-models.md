# ADR-0009 — Reporting reads through views it owns
Status: Accepted · Decision ref: D-56

## Context
Dashboards need data from contracts, jobs and billing, but modules may not import each other.

## Decision
The `reporting` module owns read-only SQL views (and, when needed, materialized views refreshed by
scheduled tasks) created in its migrations over other modules' tables. Views are subject to the same RLS
(views run with `security_invoker = true`). No module writes through them; if a source table changes
shape, the owning slice updates the dependent view in the same commit (the architecture test lists view
dependencies).

## Consequences
- Fast dashboards without a second datastore; a warehouse can come later.
- A narrow, documented exception to module ownership, limited to read-only views in `reporting`.
