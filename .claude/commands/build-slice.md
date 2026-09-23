---
description: Build one vertical slice (UI included) per the plan, the maintainable way.
argument-hint: [slice-id]
---

Implement **$1**. Obey `CLAUDE.md`. Document paths are in `kit.json`.

1. **Orient:** NOW.md, CODEBASE_MAP.md, PROGRESS.md, TECH_DEBT.md, docs/adr/, the slice in the plan, the
   data-contract sections, its screens in the experience spec and screen registry, the REQs it cites, and
   the target module's code. If the slice is only an outline, stop and ask for it to be detailed.
2. **Resume state:** `git status`, `git log --oneline`; predecessors ACCEPTED; no UI debt.
3. **Plan, then STOP for approval:** files by module (backend + frontend); schema changes (data contract
   first); ports; invariants and how each is honoured; new error codes and config keys; screens (SCR-ids
   and states); failure-path tests; REQ ids covered.
4. **Screens first:** set the slice IN_PROGRESS (PROGRESS.md and NOW.md). Create each screen's route and
   component with its `data-screen="SCR-…"` marker (loading/empty states are fine at first) and its
   Playwright spec tagged `@SCR-…` and `@REQ-…`, against the real API, at phone and desktop.
5. **Build backend and frontend together**, endpoint by endpoint, until the specs pass. Never mock the API
   in e2e. Stay inside the module boundary.
6. **Test failure paths** for every invariant touched. Commit screenshots via the e2e helper.
7. **Verify:** `bash scripts/verify.sh` — all tiers green, kit checks green.
8. **Review:** run the slice-reviewer agent; fix what it blocks.
9. **Record & commit:** PROGRESS.md (`ACCEPTED`), NOW.md (body + header), TECH_DEBT.md, CODEBASE_MAP.md,
   requirement statuses (`building` → `built`); ADRs. One commit `<slice-id>: <summary>`.
10. **Hand off:** verify summary, screenshot paths, REQs advanced, anything waiting on the owner.
