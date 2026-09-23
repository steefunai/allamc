---
description: Weekly review — what shipped, feedback triage, requirement changes, next 3 slices, NOW.md refresh.
---

Read `kit.json`, `docs/PROCESS.md`, `NOW.md`, the requirement register, `PROGRESS.md`, `TECH_DEBT.md`,
the decision log, and every file in `docs/feedback/` newer than `last_weekly_review`. Run
`git log --oneline --since=<last_weekly_review>` and `bash scripts/verify.sh`.

Produce, then STOP for my decisions:
1. **Shipped:** slices ACCEPTED since last review, with screenshot paths (phone + desktop).
2. **Health:** verify result; new TECH_DEBT; UI debt (should be 0); guardrail-file diffs (should be none).
3. **Feedback triage:** each untriaged FB item → existing REQ / new REQ / no action, with severity × frequency.
4. **Requirement changes:** new REQs, status moves with evidence, priority moves, hardening promotions (§5).
5. **Stage gate:** criteria met / not met.
6. **Next 3 slices** by PROCESS.md §4 ordering, each with REQ ids and one line on why now.
7. **Waiting on owner:** updated list. **Pause rule:** warn if `last_user_session` is 14+ days old.

After I respond, apply only what I approved; update NOW.md including every header field
(`verify`, `ui_debt`, `last_weekly_review`, `updated`, …). One commit: `review: YYYY-MM-DD`.
