# REBUILD_NOTES.md — allamc v2 started from the product kit

Decision D-80: allamc is rebuilt from the kit starting at Stage 0. The v1 repo (BOOT-001 + VS-001 in
progress) is **archived as reference, not authority**.

## What carries forward
- **Decisions D-01…D-75** from v1 discovery — kept in the decision log. Product decisions keep their status.
  Technical decisions D-70…D-75 are re-confirmed in the technical rounds after Stage 1.
- **Requirements** — re-prioritised around the thin core loop (requirements.md).
- **v1 documents** — copy them into `docs/archive/v1/` for reference: engineering plan, DATA-001,
  PRODUCT_EXPERIENCE_SPEC, AUTHORITY_REQUIRED_CONFIG, ADRs 0001–0011, and the VS-001 plan with its approval
  conditions.

## What gets harvested at BOOT-001 (through slices, never pasted in wholesale)
- verify suites → `scripts/verify.d/10-backend.sh`, `20-frontend.sh`, `50-invariants.sh` (money-float,
  audit-session, tenancy, PII and error-code backstops; import-linter contracts)
- RLS pattern: runtime role without BYPASSRLS, FORCE RLS, architecture test and its self-test
- money helper + tests (integer paise, basis points, half-up rounding, GST split)
- `tenant_session()`, config registry with CONFIG_NOT_SET, idempotent commands, PII-free logging
- the frozen job-queue migration lesson; the Windows lessons (uv PATH, LF endings, DB port from `.env` only)
- design tokens and the Styling Contract, after the prototype confirms or changes them

## What does not carry forward
- The v1 slice order (re-planned with `/propose-slices` after Stage 1).
- Any screen design not validated by the prototype.
