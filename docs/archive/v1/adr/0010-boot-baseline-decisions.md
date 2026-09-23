# ADR-0010 — BOOT-001 baseline decisions
Status: Accepted · Slice: BOOT-001 · Decision refs: D-70, D-71, D-74

## Context
BOOT-001 must leave a green `verify.sh`, including the architecture template's RLS tests, before any
domain slice exists. Several choices were not fixed by the plan or DATA-001.

## Decisions

1. **`tenant` and `branch` are created in BOOT-001, in their exact DATA-001 shape, with no API.**
   The architecture template's `seeded_two_tenants` fixture and `test_unset_tenant_context_sees_no_rows`
   query `branch`, and every tenant table's FK points at `tenant`. The models live in
   `app/modules/identity/models.py` (the owning module); VS-001 adds behaviour and the rest of identity.

2. **`config_value` is modelled in `app/common/config.py`**, not the `settings` module. The runtime
   reader `config.require_*` belongs to `app.common`, which may not import modules (import-linter). The
   `settings` module (VS-003) writes values through a port. DATA-001 §2 still lists the table under
   settings for ownership of the *write* path. Its RLS: platform rows readable by all, writable only by the
   owner role; tenant rows read/written only in their tenant's context.

3. **Every tenant-RLS table also gets an `owner_maintenance` policy `TO CURRENT_USER`** (the migrating
   owner role) via `app/common/rls.py`. With `FORCE ROW LEVEL SECURITY` the owner is subject to policies
   too; on Cloud SQL the owner is not a superuser, so without this, migrations, seeds and audited
   platform-admin paths (ADR-0002) could not work. `allamc_app` never matches this policy; the
   architecture test and the startup check still guarantee the runtime role cannot bypass RLS.

4. **Enums as `text + CHECK` are generated from the Python `StrEnum`** (`app.common.db.enum_check`), and
   an integration test compares the database constraint with the enum.

5. **Tailwind v4 with a generated `@theme`** (`frontend/scripts/gen-tokens.mjs` → `src/shared/ui/tokens.css`)
   instead of `tailwind.config.ts`. v4 is the current stable line and is configured in CSS. Colour,
   radius, shadow, type-scale, font and breakpoint defaults are reset, so only Styling Contract tokens
   compile for those. **Spacing is the PES §5 "4 px base scale"**: `--spacing: 4px` makes every
   multiple of 4 px available (e.g. layout widths `w-64` = 256 px), which is broader than the enumerated
   `space` list in `design-tokens.json`; named sizes (`touch-min`, `row-phone`, `icon`…) are tokens.
   ESLint rules (tested in `scripts/lint-rules.test.mjs`) ban raw hex, arbitrary values, inline styles
   and literal UI text.

6. **Status chips put the tone on the background and icon, with the label in `text` colour.** Some soft
   tone pairs in `design-tokens.json` (e.g. light `success` on `success-soft`) fall just under 4.5:1 for
   14 px text; axe in Playwright caught it. The tokens are unchanged.

7. **TypeScript is pinned to 5.9** (not 6.x) because `openapi-typescript` and typescript-eslint peer on 5.x.

8. **Local Postgres host port is `${DB_PORT:-5432}`** (`docker-compose.yml`). *Amended by BOOT-001-fix:*
   the first cut hard-coded 5440; now compose and the backend's local default URLs read the same
   `DB_PORT` variable (default 5432), nothing in code/tests/CI names another port, and CI keeps 5432.

9. **New error code `INTERNAL_ERROR`** (DATA-001 §9) for unhandled failures; the envelope never includes
   exception text.

10. **The error contract is published in OpenAPI.** Every route documents a `default` response
    `ErrorEnvelope {code: ErrorCode, message_key, details, request_id}`, so the generated client carries
    the `ErrorCode` union and the frontend i18n test checks translations against the committed
    `openapi.json` (no reaching into backend sources). `ApiError` still accepts unknown codes at runtime
    (older client, newer server) and shows the generic message.

11. **Design Fitness #3 on phone.** The bottom bar has no room for inline reason text, so a disabled
    bottom-bar item carries the reason as screen-reader text and shows it in a toast on tap; the "More"
    sheet shows the reason inline under the label. Desk uses a tooltip (PES §6 #3).

12. **Migration 0001 is self-contained:** it runs a frozen copy of Procrastinate 3.9.0's `schema.sql`
    (`20260923_0001_procrastinate_schema.sql`) and inlines its RLS DDL instead of calling
    `app.common.rls`, so neither a dependency bump nor a helper edit can change a merged revision. A unit
    test fails when the installed Procrastinate version differs from the frozen one.

## Consequences
- VS-001 extends `tenant`/`branch` with forward-only migrations; it must not recreate them.
- Every future tenant table uses `enable_tenant_rls()` in its migration.
- Changing the Styling Contract means editing `docs/design-tokens.json` only; the CSS is regenerated on
  build/test.
