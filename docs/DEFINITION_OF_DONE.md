# Definition of Done (kit default — products may add, never remove)

## Slice
- [ ] Traces to REQs and the slice's stories; no foreign scope.
- [ ] Inside its module boundary; boundary checks green.
- [ ] Day-one invariants honoured; failure-path tests for them exist and pass.
- [ ] Unit, integration (real DB) and e2e (real API, phone + desktop) green.
- [ ] **UI gate:** every SCR of the slice exists (`data-screen` marker), has a tagged e2e spec, and
      committed screenshots at phone and desktop — enforced by `scripts/check_ui_gate.py` (R1–R8).
      Backend-only delivery is exactly `backend-complete, UI pending` and blocks later slices.
- [ ] `bash scripts/verify.sh` green; output pasted as evidence.
- [ ] One commit with the slice id; PROGRESS.md, NOW.md, TECH_DEBT.md, CODEBASE_MAP.md updated; ADR for
      non-obvious decisions; data contract amended first for schema changes.

## Stage
- [ ] The stage's exit gate in PROCESS.md §2 is met and recorded by `/stage-gate`.
