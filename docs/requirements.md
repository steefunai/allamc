# requirements.md — allamc requirement register (v2, Stage 0)

One row per requirement, written as an outcome for a named user. Slices cite REQ ids; tests carry
`@REQ-…` tags. Change only via a commit citing the source.

**Status:** idea → to-validate → agreed → building → built → hardened (or dropped, with reason)
**Priority:** now (thin core loop) · next · later   **L:** hardening level 1–5 (PROCESS.md §5)

| ID | Requirement (who can do what, so that…) | Source | Status | Pri | L | Slices |
|---|---|---|---|---|---|---|
| REQ-001 | An owner can set up their business and first technician in under 30 minutes without help | D-01, D-50, D-61 | to-validate | now | 1 | |
| REQ-002 | An owner enters GST details and invoice numbering once, so every invoice is legally valid | D-40 | to-validate (CA) | now | 1 | |
| REQ-003 | Office staff can find or add a customer, site and AC unit by phone number in seconds, from a starter template | D-30, D-84 | to-validate | now | 1 | |
| REQ-004 | Office staff can sell an AMC contract with clear coverage from a starter template and issue its invoice | D-20, D-40 | to-validate | now | 1 | |
| REQ-005 | Preventive visits are scheduled automatically from the contract so none are forgotten | D-30 | agreed | now | 1 | |
| REQ-006 | Office staff can log a breakdown call in ≤ 3 taps and assign a technician | D-30, D-31 | to-validate | now | 1 | |
| REQ-007 | A technician can complete a job on a budget phone, in Hindi or English, with checklist, photos and customer proof | D-33, D-35, D-55 | to-validate | now | 1 | |
| REQ-008 | The customer receives a service report after every visit via a WhatsApp link | D-35, D-86 | to-validate | now | 1 | |
| REQ-009 | The business issues GST-compliant invoices and records UPI/cash payments | D-40, D-41 | to-validate (CA) | now | 1 | |
| REQ-010 | The owner sees which contracts are due for renewal and their value | D-56 | to-validate | now | 1 | |
| REQ-011 | No business can ever see another business's data | D-74 | agreed | now | 4 | |
| REQ-012 | Money is always exact to the paisa | ADR-0003 (v1) | agreed | now | 4 | |
| REQ-013 | A technician can finish a job with no mobile signal | D-34 | to-validate | next | 1 | |
| REQ-014 | Out-of-coverage work is quoted and approved before it is done | D-32 | to-validate | next | 1 | |
| REQ-015 | Customers get renewal reminders before expiry | D-22 | agreed | next | 1 | |
| REQ-016 | A business can bring its existing customers and contracts from Excel by itself | D-62, D-85 | agreed | next | 1 | |
| REQ-017 | An owner can define their own asset types and checklists without a developer | D-10, D-84 | to-validate | next | 1 | |
| REQ-018 | Customers can scan a QR sticker on the unit to request service | D-30 | idea | next | 1 | |
