---
description: Propose the next vertical slices from the requirement register using the slicing rules.
argument-hint: [how many, default 3]
---

Read `kit.json`, `docs/PROCESS.md` §4, the requirement register, `NOW.md`, the plan, the experience spec
and the screen registry. Propose ${1:-3} slices, highest priority first. For each: ID, title as
"<user> can <outcome>"; REQ ids (and which part, if split); why now (which ordering rule); screens
(existing SCR-ids or new ones, 2 lines each); acceptance e2e in one sentence; key failure paths and
invariants; out of scope; size check against §4 limits.

Reject your own proposal if it is horizontal, has no REQ, or exceeds the limits. STOP for approval; then,
with my approval for the guardrail file, add the slices to the plan, experience spec, screen registry,
PROGRESS.md and NOW.md in one commit: `slices: <ids>`.
