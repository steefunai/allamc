# requirements.md — the requirement register

One row per requirement, written as an outcome for a named user (not a feature). Agents read this
before planning; slices cite REQ ids; tests carry `@REQ-…` tags (pytest marker `req("REQ-…")`,
Playwright tag). Changes happen only via a commit that cites the source.

**Status:** `idea` → `to-validate` → `agreed` → `building` → `built` → `hardened` (or `dropped`, with reason)
**Priority:** `now` (thin core loop / current stage) · `next` · `later`
**L:** hardening level 1–5 (docs/PROCESS.md §5)

| ID | Requirement (who can do what, so that…) | Source | Status | Pri | L | Slices |
|---|---|---|---|---|---|---|
| REQ-001 | An owner can sign up their business and invite staff with the right roles, so the team can work in one system | D-01, D-50 | building | now | 2 | VS-001 |
| REQ-002 | An owner can enter GST details and invoice numbering once, so every invoice is legally valid | D-40 | agreed | now | 1 | VS-003 |
| REQ-003 | A business can describe the equipment it services and its checklists without a developer | D-02, D-10, D-11 | to-validate | now (templates only) | 1 | VS-004 |
| REQ-004 | Office staff can find or add a customer, site and asset by phone number in seconds | D-30 | agreed | now | 1 | VS-006 |
| REQ-005 | Office staff can sell an AMC contract with clear coverage and issue its invoice | D-20, D-40 | to-validate | now (one template) | 1 | VS-009, VS-010 |
| REQ-006 | Preventive-maintenance visits are scheduled automatically so none are forgotten | D-30 | agreed | now | 1 | VS-010, VS-011 |
| REQ-007 | Office staff can log a breakdown call in ≤ 3 taps and assign a technician | D-30, D-31 | to-validate | now | 1 | VS-011 |
| REQ-008 | A technician can complete a job on their phone with checklist, photos and customer proof | D-33, D-35 | to-validate | now | 1 | VS-012 |
| REQ-009 | A technician can finish a job with no mobile signal | D-34 | agreed | next | 1 | VS-013 |
| REQ-010 | The customer receives a service report after every visit | D-35, D-54 | agreed | now | 1 | VS-012, VS-015 |
| REQ-011 | The business issues GST-compliant invoices and credit notes | D-40 | to-validate (CA) | now | 1 | VS-007 |
| REQ-012 | Out-of-coverage work is quoted and approved before it is done | D-32 | to-validate | next | 1 | VS-014 |
| REQ-013 | The owner sees which contracts are due for renewal and their value | D-56 | agreed | next | 1 | VS-016 |
| REQ-014 | A business can bring its existing customers and contracts from Excel | D-62 | agreed | next | 1 | VS-017 |
| REQ-015 | No business can ever see another business's data | D-74 | agreed | now | 4 | all |
| REQ-016 | Money is always exact to the paisa | ADR-0003 | agreed | now | 4 | all |

Slice ids will be renumbered by plan v1.1; update the Slices column in the same commit.
