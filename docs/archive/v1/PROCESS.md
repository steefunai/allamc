# PROCESS.md — how allamc.in gets built (the operating system)

You don't need to remember this file. `NOW.md` tells you where you are, and three commands run the
rituals: `/build-slice` (per slice), `/weekly-review` (every week), `/propose-slices` (whenever the
"Next" list in NOW.md has fewer than 3 slices). This file is the reference they follow.

## 1. The chain (traceability)

```
Evidence (docs/feedback/FB-…)  →  Requirement (docs/requirements.md REQ-…)  →  Decision (PRODUCT_DECISIONS D-…)
        →  Slice (engineering plan VS-…)  →  Screens (SCR-…) + Tests (@REQ-… tags)  →  Screenshots / release
```
- Nothing gets built without a REQ. Nothing becomes a REQ without a source (evidence, law, or an
  explicit owner decision).
- Requirements change only by editing `requirements.md` in a commit that cites the evidence, and, if
  a decision changes, a superseding entry in `PRODUCT_DECISIONS.md`. Never silently.

## 2. Stages and exit gates

| Stage | Exit gate (all must be true) |
|---|---|
| 0 Frame | Brief written; core loop named; riskiest assumptions ranked |
| 1 Prototype | 5 users walked the core loop unaided; screens approved; top VALIDATE items resolved or re-scheduled |
| 2 Walking skeleton | Thin core loop deployed to staging; one real user completed it |
| 3 Design partners | 2+ partners doing real work weekly without help |
| 4 Deepen | All `now` REQs `built`; partners' top-3 pains addressed |
| 5 Harden | Every REQ at the hardening level its risk demands (see §5); security review + restore drill done |
| 6 Launch | Monitoring, runbooks, staged rollout, support process live |

The current stage and what blocks its gate are always at the top of `NOW.md`.

## 3. Cadences

**Per slice** (`/build-slice`): plan → your approval → screens + e2e specs first → build → verify →
reviewer → commit → NOW.md updated. Your part: approve the plan (≈5 min), look at the screenshots
(≈5 min), say "accept" or what's wrong.

**Weekly** (`/weekly-review`, same day each week, ≈45 min of your time):
1. Partner/user session (30 min): watch them use staging; write raw notes in `docs/feedback/`.
2. Run `/weekly-review`: the agent compiles what shipped, screenshots, new tech debt, untriaged
   feedback, requirement changes it proposes, and the next 3 slices.
3. You decide: accept/adjust requirement changes and the next slices. The agent commits them.

**Monthly / at each stage gate:** check the gate table above; revisit every `to-validate` REQ and
every VALIDATE decision; re-rank `next` vs `later`; review TECH_DEBT and schedule the top items.

## 4. Deciding slices

A slice is **the smallest change that lets a named user do something end-to-end they couldn't do
before, visible in the UI, demonstrable in under 2 minutes.**

Size limits (split if exceeded): one page of plan · ≤ 4 screens · ≤ 1 new module or port · one
migration · roughly 1–3 days of agent work.

Order by, in this priority:
1. **Core loop first, thin.** Until the whole loop works end to end, only loop slices.
2. **Riskiest assumption next.** Prefer the slice that teaches you the most (a VALIDATE item).
3. **Partner pain.** Frequency × severity from the feedback log.
4. **Cost of delay.** Legal/compliance before go-live, and anything blocking a partner.
5. **Dependencies** break ties, never override the above.

How to split a big requirement:
- by **workflow step** (log job → assign → execute);
- by **role** (office first, technician next);
- **happy path first, then variations** — but invariant failure paths (tenancy, money, audit,
  locking) are never deferred;
- **one variant before many** (one contract template before the rule builder);
- **manual before automated** (dispatcher assigns before auto-assign);
- **online before offline**, **in-app before messaging**.

Never slice horizontally ("backend for X", "UI for X"). The only slice without user value is BOOT.

## 5. Hardening levels (per REQ, column `L` in requirements.md)

L1 documented · L2 tested (incl. failure paths) · L3 checked (lint/architecture/diff checks) ·
L4 impossible (types, DB constraints, RLS, triggers) · L5 watched (monitors, reconciliation).

Promote a REQ when it has survived 2–3 iterations unchanged, when money/legal/security depend on it,
when an expert signed it off, or when it broke in production (then fix the class, not the instance).
Day-one invariants (tenancy, money types, audit, auth, IDs, time zones, i18n strings, PII) start at L4.

## 6. Guardrails on the guardrails

Agents may not edit `scripts/verify.sh`, `scripts/check_ui_gate.py`, `docs/screen-registry.json`,
`docs/requirements.md` statuses, or `PROCESS.md` without your explicit approval in that session.
Any diff to them is called out at the top of the hand-off.
