# Definition of Done — allamc.in

Two levels: a **slice** is done when its checklist passes; a **release track** (MVP-1 / MVP-2 / T2…) is
done when all its slices are done AND the track-level checks pass. "Done" is judged by evidence, not by
what could be mechanically run.

## Slice-level Definition of Done

A slice is ACCEPTED only when every box is true and evidenced:

- [ ] Implements only behaviour traced to the slice's stories in `engineering-plan-v1.0.md` (and the
      `PRODUCT_DECISIONS.md` entries behind them). No foreign scope.
- [ ] Stays within its module boundary; cross-domain needs go through `app/ports/` (import-linter green).
- [ ] Honors every applicable integrity invariant (tenancy/RLS, audit co-transactional, optimistic lock,
      money-as-integers, AUTHORITY_REQUIRED config, idempotent commands, immutable versions/documents,
      PII). See `CLAUDE.md` §2 and DATA-001 §5.
- [ ] New tenant-owned tables have `tenant_id` + FORCE RLS; the architecture test passes; the
      cross-tenant integration harness covers every new endpoint.
- [ ] Unit + component tests pass for the changed code.
- [ ] **Failure-path tests** listed for the slice in the plan exist and pass (not happy-path only).
- [ ] Integration tests pass against real Postgres (never SQLite, never mocks of the DB).
- [ ] E2E (Playwright) acceptance test proves the slice's user-visible behaviour end to end.
- [ ] **UI surface gate (below) satisfied, or the slice is labelled exactly `backend-complete, UI pending`.**
- [ ] `bash scripts/verify.sh` passes (ruff, mypy, import-linter, pytest unit+integration, tsc, ESLint,
      Vitest, Playwright, invariant backstops).
- [ ] Test output pasted as evidence in the hand-off.
- [ ] One commit, slice id in the message; `PROGRESS.md`, `TECH_DEBT.md`, `CODEBASE_MAP.md` updated; ADR
      for any non-obvious decision, schema change, or contract deviation; DATA-001 amended first when
      schema/enums/state machines change.

## UI surface gate

For each slice, first answer in the plan: **does this slice have screens in
`PRODUCT_EXPERIENCE_SPEC.md`?**

- **If NO** (e.g. VS-002 audit ledger, OPS-001): N/A. Proceed.
- **If YES**, the slice is not ACCEPTED until:
  - [ ] every named SCR-id exists and renders at **360 px and 1280 px**, light and dark theme,
  - [ ] wired to the real endpoints (no mock data outside tests),
  - [ ] uses only Styling Contract tokens (`design-tokens.json`) — no competing design system,
  - [ ] passes all ten **Design Fitness** checks (spec §6),
  - [ ] loading / empty / error / offline / no-permission states implemented,
  - [ ] en + hi translations complete,
  - [ ] a component test (with axe) and an e2e test cover each screen's primary path.
- Backend delivered without UI → `PROGRESS.md` status **exactly** `backend-complete, UI pending`, missing
  screens listed in `TECH_DEBT.md`. It does not count toward track completion.

## Release-track Definition of Done

- [ ] Every slice in the track is ACCEPTED (none `backend-complete, UI pending`).
- [ ] `verify.sh` clean repo-wide from a clean checkout: `docker compose up -d`, `alembic upgrade head`,
      seeds, full suite.
- [ ] Every AUTHORITY_REQUIRED key the track uses is documented in `AUTHORITY_REQUIRED_CONFIG.md`, and
      production values are set by an Admin (none defaulted in code).
- [ ] Performance budgets and accessibility checks from plan §8 pass.
- [ ] Restore drill from backup executed on staging and recorded.
- [ ] Validation tasks that gate this track (plan §9) are closed with notes.
- [ ] `PROGRESS.md` shows the whole track ACCEPTED.

The word reserved for finished work is **ACCEPTED**. Do not describe a slice or track as finished while
it has any `UI pending`, any red test, any un-run test tier, or any unlogged deferral. `verify.sh`
rejects `PROGRESS.md` lines that use the bare word for finished work.
