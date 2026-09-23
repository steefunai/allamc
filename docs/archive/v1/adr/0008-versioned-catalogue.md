# ADR-0008 — Immutable published versions for tenant-defined schemas
Status: Accepted · Decision refs: D-10, D-12, D-20

## Decision
Asset-type field schemas, checklists and coverage rule sets are stored as versions. Drafts are editable;
publishing freezes a version (DB trigger rejects UPDATE of published rows). Assets, contracts and jobs
pin the version they were created with.

## Consequences
- Service reports and billing decisions are reproducible forever.
- Moving existing assets to a newer schema is an explicit, audited "upgrade" action (future slice),
  never implicit.
