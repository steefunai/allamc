# PROCESS.md — the product-building operating system (kit-owned)

You don't need to remember this file. `NOW.md` says where the product is; five commands run the
rituals: `/frame-product` (Stage 0), `/build-slice` (per slice), `/weekly-review` (weekly),
`/propose-slices` (when NOW.md shows < 3 next slices), `/stage-gate` (when you think a stage is done).
Document paths come from `kit.json`.

## 0. The idea
Quality comes from two loops. **Build the thing right** — code checked against the spec by tests,
types, checks and review; agents are strong here if the checks are hard. **Build the right thing** —
the spec checked against real users; only the owner can run this loop. Both run every week.

## 1. The chain (traceability)
```
Evidence (feedback FB-…)  →  Requirement (REQ-…)  →  Decision (D-…)  →  Slice (VS-…)
        →  Screens (SCR-…) + tests tagged @REQ-… / @SCR-…  →  screenshots / release
```
Nothing is built without a REQ; nothing becomes a REQ without a source (evidence, law, or an explicit
owner decision). Requirements and decisions change only in a commit citing the source; decisions are
superseded, never edited.

## 2. Stages and exit gates
| Stage | Exit gate |
|---|---|
| 0 Frame | Brief written; one core loop named; riskiest assumptions ranked; decisions tagged DECIDED / DEFAULT / VALIDATE |
| 1 Prototype | 5 target users completed the core loop in a clickable prototype unaided; screens approved; top VALIDATE items resolved or scheduled |
| 2 Walking skeleton | Thin core loop, production-shaped (auth, DB, CI, deploy, day-one invariants), on staging; one real user completed it |
| 3 Design partners | 2+ partners doing real work weekly without help |
| 4 Deepen | All `now` REQs `built`; partners' top-3 pains addressed |
| 5 Harden | Every REQ at the level its risk demands (§5); external security review and a backup-restore drill done |
| 6 Launch & operate | Monitoring, runbooks, staged rollout, support process live |

**Day-one invariants** (in the skeleton, at L4, never deferred): data isolation between customers,
money/number types, ID scheme, time zones, externalised UI strings, auth & permission model, one error
format, forward-only migrations, secrets handling, no personal data in logs, audit history for anything
legal or financial.

## 3. Cadences
- **Per slice** — `/build-slice`: plan → owner approval → screens + e2e specs first → build →
  `verify.sh` → independent review → one commit → NOW.md updated. Owner: approve plan (~5 min), look at
  screenshots (~5 min).
- **Weekly** — user session (30 min, watch them use staging, notes in `docs/feedback/`), then
  `/weekly-review` and decide (15 min).
- **Monthly / stage end** — `/stage-gate`; revisit every VALIDATE decision and `to-validate` REQ;
  re-rank next vs later; schedule top tech debt.
- **Pause rule** — two weeks without a user session → stop building features until contact resumes.

## 4. Deciding slices
A slice is **the smallest change that lets a named user do something end to end they couldn't before,
visible in the UI, demonstrable in under 2 minutes.**
Split if over: one page of plan · 4 screens · 1 new module/port · 1 migration · ~1–3 days of agent work.
Order by: (1) core loop first, thin; (2) riskiest assumption; (3) partner pain = frequency × severity;
(4) cost of delay (compliance, blockers); (5) dependencies only break ties.
Split by: workflow step · role · happy path then variations (invariant failure paths never deferred) ·
one variant before many · manual before automated · online before offline · in-app before messaging.
Never horizontal ("backend for X"). Only BOOT has no user value.

## 5. Hardening levels (column `L` in the requirement register)
L1 documented · L2 tested incl. failure paths · L3 checked (lint, architecture, API-diff) ·
L4 impossible (types, DB constraints, RLS, triggers) · L5 watched (monitors, reconciliation jobs).
Promote when a REQ survived 2–3 iterations unchanged, when money/legal/security depend on it, when an
expert signed it off, or when it broke in production (fix the class, not the instance). Don't harden
what is still changing. Techniques by payoff: property-based tests · mutation testing on core domain ·
state-machine tests · concurrency tests · contract tests at boundaries · golden files for documents ·
visual regression · API/schema diff checks · abuse tests + security review · load tests + restore drills
· production monitors, feature flags, staged rollouts.

## 6. Working with coding agents
1. Plan before code. 2. Vertical slices, UI included. 3. Acceptance test first, from the user's side.
4. Enforce in tools, not prose. 5. Two strikes → a check. 6. Agents never edit guardrails (deny rules
in `.claude/settings.json` + CODEOWNERS). 7. One source of truth per question (kit.json lists them).
8. Independent review with fresh context. 9. Evidence, not claims. 10. Git is the memory.
11. Log deferrals honestly. 12. The owner's time goes to judgment: users, flows, screenshots, plans.

## 7. Multiple products
One repo per product created from this kit; one Claude Project per product (knowledge = brief,
decisions, requirements, NOW.md; instructions = the standard block in the kit README); a new chat per
topic. Every NOW.md carries the machine-readable header so the portfolio script can read it. Keep at
most 1–2 products in active build; others in *discovery* or *maintain*.
