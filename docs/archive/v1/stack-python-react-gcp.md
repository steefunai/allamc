# Stack — Python (FastAPI) + React (Vite PWA) on Google Cloud

Library versions: take the latest stable release at BOOT-001 and pin them in `uv.lock` and
`package-lock.json`. Upgrades are their own commits with the full suite green.

## 1. Repository layout

```
/
├─ CLAUDE.md · AGENTS.md · PROGRESS.md · TECH_DEBT.md · CODEBASE_MAP.md · README-SETUP.md
├─ docker-compose.yml            # local Postgres 16 (+ db-init.sql)
├─ .env.example
├─ docs/                         # plan, DATA-001, PES, tokens, DoD, config, ADRs, runbooks
├─ scripts/verify.sh · scripts/db-init.sql
├─ infra/                        # Terraform (OPS-001)
├─ backend/
│  ├─ pyproject.toml · uv.lock · .importlinter · alembic.ini
│  ├─ alembic/versions/
│  ├─ app/
│  │  ├─ main.py                 # FastAPI app factory; routers mounted per module
│  │  ├─ wiring.py               # composition root: binds port Protocols to implementations
│  │  ├─ worker.py               # Procrastinate app + scheduled tasks
│  │  ├─ common/                 # errors, money, db/tenant_session, config, ids, clock, auth deps, logging, pagination
│  │  ├─ ports/                  # Protocols only: audit, billing, coverage, stock, notification, payment_gateway, oem_connector …
│  │  ├─ seeds/                  # dev_test_config, starter templates, role templates
│  │  └─ modules/<module>/
│  │     ├─ api.py               # FastAPI router (thin: auth, parse, call service, map result)
│  │     ├─ schemas.py           # Pydantic request/response models (StrictInt for money)
│  │     ├─ models.py            # SQLAlchemy models (this module's tables only)
│  │     ├─ repository.py        # queries; no business rules
│  │     ├─ service.py           # use-cases; transactions; audit; split into services/*.py past ~300 lines
│  │     ├─ adapters.py          # implementations of ports this module provides
│  │     ├─ enums.py · tasks.py (background jobs) · json_schemas/
│  └─ tests/
│     ├─ unit/<module>/ · integration/<module>/ · architecture/
│     └─ conftest.py             # DB fixtures, tenant factories, cross-tenant harness
└─ frontend/
   ├─ package.json · vite.config.ts · playwright.config.ts · tailwind.config.ts (from design-tokens.json)
   ├─ src/
   │  ├─ app/                    # routes, shell, providers, role-based navigation
   │  ├─ shared/
   │  │  ├─ ui/                  # design system on Radix primitives + tokens
   │  │  ├─ api/                 # typed client generated from OpenAPI (openapi-typescript) + fetch wrapper
   │  │  ├─ i18n/                # en.json, hi.json, error-code messages
   │  │  ├─ money.ts             # Paise branded type, formatPaise, parseRupeesInput → Paise
   │  │  ├─ offline/             # Dexie db, outbox, media queue, sync engine
   │  │  └─ auth/
   │  └─ features/<module>/      # screens, hooks, components for that module only
   └─ e2e/                       # Playwright specs per slice
```

## 2. Backend patterns

- **Request lifecycle:** auth dependency resolves the principal (user, tenant, roles, scopes) from the
  access token → `tenant_session(principal)` opens a transaction on the `allamc_app` engine and runs
  `SET LOCAL app.tenant_id = :tid` → service runs → commit. One transaction per request unless a slice
  documents otherwise.
- **Two engines:** `owner_engine` (migrations and platform-admin tasks only, never in request handlers)
  and `app_engine` (`allamc_app`, NOBYPASSRLS). Startup refuses to serve if `app_engine`'s role owns
  tables or has BYPASSRLS.
- **Background jobs** (Procrastinate on Postgres): enqueue inside the business transaction so the job
  exists iff the change committed. Every task receives `tenant_id` explicitly and opens its own
  `tenant_session`. Periodic tasks (PM generator, expiry, reminders) are idempotent by natural keys.
- **Ports:** a Protocol in `app/ports/x.py`, implemented in the owning module's `adapters.py`, bound in
  `wiring.py`, injected via FastAPI dependencies. Ports accept/return plain dataclasses or Pydantic
  models defined in `app/ports/`, never another module's ORM objects.
- **Errors:** raise `AppError(ErrorCode.X, details=...)`; the handler maps to HTTP status and returns
  `{code, message_key, details, request_id}`.
- **Optimistic locking:** `__mapper_args__ = {"version_id_col": version}`; clients send `version` with
  every mutating request; `StaleDataError` → 409 `VERSION_CONFLICT`.
- **Money:** `app/common/money.py` (reference in `docs/templates/money_reference.py`); Pydantic fields
  `StrictInt`; API accepts paise integers only (the frontend converts user input with
  `parseRupeesInput` using string arithmetic, never float).
- **OpenAPI** is the contract for the frontend; the typed client is regenerated in `verify.sh` and must
  produce no diff.
- **Auth:** Google Identity Platform for phone OTP and email/password; backend verifies the ID token once
  and issues its own short-lived access token + rotating refresh token; permissions checked with
  `require_permission("jobs.assign")` dependencies that also return the scope filter.
- **Files:** uploads go directly from the browser to Cloud Storage with a signed PUT URL; the API records
  `storage_key` + `sha256` after upload; downloads via short-lived signed GET URLs.
- **PDFs:** HTML templates rendered server-side (WeasyPrint) with embedded Inter + Noto Sans Devanagari.
- **Logging:** structlog JSON; a filter drops known PII fields; include `request_id`, `tenant_id`,
  `user_id`, `route`, `duration_ms`.

## 3. Frontend patterns

- **Routing** by area (`/app/...` office, `/tech/...` technician, `/p/...` public) with role guards.
- **Server state** with TanStack Query; mutations send `version`; on 409 show the "changed by someone
  else" pattern with reload/compare.
- **Offline (technician area):** Workbox precache of the app shell + technician routes; Dexie tables for
  jobs, checklists, assets, outbox, media queue; sync engine replays the outbox in order per job on
  `online` events, on app focus and on a timer; Background Sync where supported.
- **Money:** `type Paise = number & { readonly __brand: "Paise" }`; values are safe integers
  (< 2^53 paise); `formatPaise(p)` uses `Intl.NumberFormat("en-IN", { style: "currency", currency:
  "INR" })` on the rupee/paise parts computed with integer maths.
- **Forms:** react-hook-form + zod schemas generated or aligned with OpenAPI.
- **i18n:** react-i18next; keys namespaced by feature; `hi.json` must have every key (checked in Vitest).
- **Lint:** ESLint with `no-restricted-imports` preventing `features/a` → `features/b` internals and
  rules banning raw hex colours / arbitrary Tailwind values.

## 4. Testing tiers

| Tier | Tool | Scope | Runs in |
|---|---|---|---|
| Unit | pytest (`-m unit`), Vitest | pure logic: money, coverage resolver, state machines, schema validation, components | pre-commit, CI |
| Integration | pytest (`-m integration`) against real Postgres | repositories, services, RLS, triggers, locking, idempotency, API routes via httpx | CI (and locally with DB) |
| Architecture | pytest + import-linter | module boundaries, RLS on every table, no float money columns | pre-commit, CI |
| E2E | Playwright (Chromium, mobile + desktop viewports) | slice acceptance through the real UI + API + DB | CI (and locally with DB) |

Every integration test runs inside a transaction rolled back at the end, **as `allamc_app`**, with the
tenant context set — exactly like production.

## 5. Google Cloud deployment

| Concern | Service |
|---|---|
| API + worker | Cloud Run (`api`, `worker`), region asia-south1, min instances 1 for `api` in prod |
| Database | Cloud SQL for PostgreSQL 16, private IP, PITR, automated backups; nightly export to a bucket in asia-south2 |
| Files | Cloud Storage buckets `media` and `documents` (uniform access, lifecycle rules) |
| Frontend | Firebase Hosting (CDN) with SPA rewrites and strict CSP |
| Scheduling | Cloud Scheduler → authenticated worker endpoints (or Procrastinate periodic tasks) |
| Auth | Identity Platform (phone + email providers) |
| Secrets | Secret Manager (DB passwords, gateway keys, tenant WhatsApp tokens by reference) |
| CI/CD | GitHub Actions: verify → build image (Artifact Registry) → migrate job → deploy; Workload Identity Federation |
| Observability | Cloud Logging, Cloud Monitoring alerts, Error Reporting or Sentry |
| IaC | Terraform in `infra/` |
