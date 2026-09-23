# CLAUDE.md — {{PRODUCT}} project rules

The law of this codebase. Short on purpose: it points at the documents listed in `kit.json`.
(Codex: identical rules in `AGENTS.md`.)

## Base authority
- **Where we are:** `NOW.md` — read first, every session.
- **WHAT & order:** the plan; **schema/invariants:** the data contract; **screens:** the experience spec;
  **WHY:** the decision log and `docs/adr/`; **requirements:** the register. Paths in `kit.json`.
- **HOW:** this file. **Process:** `docs/PROCESS.md`.
- **Guarantees:** `scripts/verify.sh` (+ `scripts/verify.d/*`), the UI gate, CI, database constraints.
- If documents conflict, stop and ask.

## 0. Orientation
Read NOW.md, CODEBASE_MAP.md, PROGRESS.md, TECH_DEBT.md, docs/adr/, the slice in the plan, the relevant
data-contract sections, its screens, the REQs it cites, and the existing code of the one module you'll
change. Match existing patterns.

## 1. Boundaries
<!-- PRODUCT: list modules and how they may depend on each other; name the enforcing tool. -->
- Modules never import each other's internals; cross only through declared ports/interfaces.
- No invented domain concepts, tables, screens or capabilities beyond the plan; gap-fills go in
  TECH_DEBT with justification.
- Errors use the central error-code list, never inline strings.

## 2. Day-one invariants (a defect even if tests pass)
<!-- PRODUCT: make each concrete (tool, type, constraint). Remove none without an ADR. -->
- Data isolation between customers/tenants, enforced below application code.
- Exact money/number types; one rounding helper.
- Audit history for legal/financial changes, written in the same transaction.
- Optimistic concurrency on contended records.
- Business/tax/security values are AUTHORITY_REQUIRED config, never literals.
- Forward-only migrations; issued documents immutable; no personal data in logs.

## 3. Definition of Done
`docs/DEFINITION_OF_DONE.md`. UI slices build screens and tagged e2e specs **first**, then fill them in
as the API grows. Evidence (verify output + screenshot paths) in every hand-off.

## 4. Rhythm
Plan mode → approval → one slice at a time → verify → reviewer → one commit → update PROGRESS.md,
NOW.md (including its header), TECH_DEBT.md, CODEBASE_MAP.md. Resume from git, never memory.
Never edit guardrail files (see kit.json `kit_owned_files`, CODEOWNERS) unless the owner explicitly
approves in this session; call out any such diff at the top of the hand-off.
