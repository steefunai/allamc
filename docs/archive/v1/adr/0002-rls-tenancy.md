# ADR-0002 — Shared-schema multi-tenancy enforced by Postgres RLS
Status: Accepted · Decision ref: D-74

## Context
Thousands of small tenants, a few large ones, one small team. Options: database-per-tenant,
schema-per-tenant, shared schema with `tenant_id`.

## Decision
Shared schema with `tenant_id` on every tenant-owned table, **ENABLE + FORCE ROW LEVEL SECURITY**, policy
on `app_current_tenant()` (from `SET LOCAL app.tenant_id`). Runtime connects as `allamc_app`
(NOSUPERUSER, NOBYPASSRLS, owns nothing). Migrations run as the owner role.

## Consequences
- A missing `WHERE tenant_id` in application code cannot leak data; an unset context returns no rows.
- Every table needs a policy: the architecture test enforces it.
- Background tasks must set tenant context explicitly; cross-tenant platform reports use the owner
  engine in dedicated, audited platform-admin code paths only.
- Large-tenant isolation (dedicated DB) remains possible later by routing a tenant to another instance.
