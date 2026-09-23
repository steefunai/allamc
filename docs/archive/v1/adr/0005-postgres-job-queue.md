# ADR-0005 — Postgres-backed background jobs (Procrastinate); Redis deferred
Status: Accepted · Decision ref: D-75

## Context
Needed: reminders, PM generation, PDFs, message sending, webhook processing. A solo builder should run
as few managed services as possible, and jobs must exist iff the business transaction commits.

## Decision
Procrastinate on the same Postgres. Jobs are deferred inside the business transaction. Periodic tasks
are idempotent. Redis is added only when a measured need (caching, rate-limit counters at scale)
appears, via a new ADR.

## Consequences
- The kit's CI Redis service is not required; `verify.yml` omits it until then.
- Queue depth/lag is monitored in Postgres; heavy workloads may later move to Cloud Tasks.
