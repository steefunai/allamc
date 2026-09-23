# PRODUCT_DECISIONS.md — allamc decision log

This is the decision log. D-01…D-75 come from the v1 discovery quiz and carry forward into v2 (see
REBUILD_NOTES.md); D-80 onward are v2 Stage 0 decisions. The engineering plan implements these
decisions; the slice-reviewer uses this file to check lineage ("does this change trace to a decision?").
Changing a decision requires a new entry that supersedes the old one, never a silent edit.

Status legend: **DECIDED** (owner chose) · **DEFAULT** (architect proposed, owner accepted by delegation)
· **VALIDATE** (decided provisionally; must be confirmed with real users/advisors before its track starts).

## Market & scope

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-01 | allamc.in serves **independent multi-brand service businesses, OEM-authorised service centres, and end customers (marketplace)**. | DECIDED | Three-sided platform; sequenced by release tracks (D-03). |
| D-02 | **Any product category**, configured by tenants — no hard-coded asset types. | DECIDED | Metadata-driven `catalogue` module; nothing references product-specific columns. |
| D-03 | Launch order: **(1) SaaS for independents → (2) OEM features → (3) customer app → (4) marketplace.** | DECIDED | Each track brings the data the next one needs. |
| D-04 | All business sizes via **tiered plans** (Starter / Growth / Enterprise). | DECIDED | Entitlements are config (D-40). |
| D-05 | Marketplace monetisation: **commission on AMCs sold/renewed online through allamc.in**; listing free for subscribers; **no paid leads**. | DEFAULT · VALIDATE | Requires split-payment gateway and GST e-commerce-operator review by a CA before track 4. Only design-in now: tenant AMC plans are publishable later. |

## Catalogue & configuration

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-10 | **Tenants build their own** asset types, fields and checklists (no-code). | DECIDED | Field builder + checklist builder screens. |
| D-11 | allamc.in ships **optional starter templates** tenants copy and own. | DEFAULT | Small shops won't start from a blank page. |
| D-12 | Asset-type, checklist and coverage-rule definitions are **versioned; published versions immutable**. | DEFAULT | Old service reports must never change after a template edit. |

## Contracts

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-20 | Contract types: **Comprehensive, Non-comprehensive, Pay-per-visit, and tenant-defined** — all modelled as one **coverage-rule engine** (labour covered, part categories, parts cap, consumables, PM visits, breakdown-call quota). | DECIDED | Job closure asks the coverage resolver what is free vs billable. |
| D-21 | Mid-term asset changes via **versioned amendments**: pro-rata charge for additions, credit-or-nothing for removals (tenant policy), **pre-inspection before coverage starts** for added assets, approval requirements configurable. | DEFAULT | Prevents "add a broken AC, claim a free compressor". |
| D-22 | Renewals: **reminders, auto-quote with uplift, or e-mandate auto-renew — tenant chooses per contract.** | DECIDED | E-mandate limits and pre-debit notice per RBI rules → config. |

## Service jobs

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-30 | Job intake MVP: **office logging (phone/WhatsApp), QR sticker public request page, auto-generated PM visits.** WhatsApp chatbot in track 3. Duplicate guard per asset. | DEFAULT | All channels create the same `job` with a `source`. |
| D-31 | Assignment MVP: **dispatcher assigns with ranked suggestions** (skill, distance, load); solo tenants auto-assign; full auto-assign and open pool later. | DEFAULT | Auto-dispatch on poor data breeds distrust. |
| D-32 | Out-of-coverage findings: **three standard flows the tenant selects per contract type** — A on-spot quote + customer OTP/link, B office approval above threshold then customer, C log & revisit. Default B. "Repair declined" captured with acknowledgement. | DECIDED + DEFAULT | Threshold is config. |
| D-33 | Technician app is an **installable PWA** from the same React codebase; Capacitor wrap later if needed. | DEFAULT | One codebase; no Play Store friction. |
| D-34 | **Offline-first job execution**: checklist, photos, voice notes, signature, "completed on device"; money collection and server OTP need connectivity; conflicts go to a dispatcher queue. | DEFAULT | Lift pits and basements have no signal. |
| D-35 | Proof of service configurable per contract type; default **GPS check-in/out (not continuous tracking), checklist-mandated photos, customer OTP online / signature offline**, auto service report. | DEFAULT | Customer receives a dispute window after offline closure. |

## Billing & inventory

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-40 | Tenants are **mostly GST-registered**; **allamc.in is their only billing system**. | DECIDED | Full GST invoicing, credit/debit notes, receipt vouchers for advances, GSTR-1 export, Tally XML export. CA review before launch (VALIDATE). |
| D-41 | Payment methods: **UPI/payment link, cash collected by technician, bank transfer/cheque on credit**. | DECIDED | Technician cash wallet + handover; cheque bounce = payment reversal. |
| D-42 | B2B **TDS deductions** handled in receivables. | DEFAULT | Otherwise every corporate customer looks overdue. |
| D-43 | E-invoicing (IRN) per tenant above the government turnover threshold, via a GSP, in track 2. | DEFAULT | Threshold is config. |
| D-44 | Stock models: **central store, van stock, or buy-per-job — tenant chooses**; one location-based engine; weighted average cost. | DECIDED | Append-only movement ledger. |
| D-45 | **Tracking level per part** (none / batch / serial); serial parts require removed-part serial + photo; defective bin in MVP-2; OEM RMA in track 2. | DEFAULT | Stops "replaced but not replaced" leakage. |
| D-46 | **Full purchasing**: suppliers, POs with approval threshold, GRN, vendor bills, purchase register (ITC). GSTR-2B reconciliation and e-way bills later. | DECIDED | |

## People, customers, communication

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-50 | **Standard roles + tenant custom roles** (permission toggles) with scope (all branches / own branches / own jobs). Some permissions Owner-only. | DECIDED | Restricted actions shown disabled with reason. |
| D-51 | **B2B customer portal in MVP-2** (OTP login: sites, assets, history, reports, invoices, pay, raise request); consumers get secure links until track 3. | DEFAULT | |
| D-52 | **Global person identity** keyed by verified phone, linked to tenant customer contacts **with consent** (DPDP). | DEFAULT | Enables track-3 "all my AMCs" without a painful migration. |
| D-53 | OEM job flow unknown → **`OEM_CONNECTOR_PORT`** with manual, email/Excel-import and per-brand API adapters. | DEFAULT · VALIDATE | Interview 5–8 OEM service centres before track 2. |
| D-54 | WhatsApp: **tenant connects their own WhatsApp Business number** (Cloud API via Embedded Signup); **one-tap send link fallback**; SMS via tenant DLT later; email. | DECIDED + DEFAULT | Confirm current Meta number/coexistence rules (VALIDATE). |
| D-55 | Languages: **English + Hindi in MVP-1**, i18n-ready for regional languages; voice notes and icon+label UI for technicians. | DEFAULT | Noto Sans Devanagari in the type stack. |
| D-56 | Owner dashboard priority: **1 renewals & revenue pipeline, 2 SLA/turnaround & repeat complaints, 3 technician productivity, 4 receivables & cash with technicians.** | DECIDED | Renewals pipeline is the home screen. |

## allamc.in's own business

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-60 | Pricing **per technician per month**, office users bundled, three feature tiers. Price points set after interviews. | DEFAULT · VALIDATE | Entitlements in config. |
| D-61 | **Free forever, capped** (1 office user, 1 technician, ~50 active contracts, limited storage) **+ 30-day Growth trial**. | DEFAULT | Seeds marketplace supply. |
| D-62 | Migration: **self-serve Excel import wizard + assisted migration** for larger tenants; batches undoable within a window; imports accept visits-consumed and opening balances. | DECIDED + DEFAULT | Assisted work uses audited, consented support access. |
| D-63 | Two separate billing systems: **tenant→customer billing** (`billing`) and **allamc.in→tenant subscriptions** (`platform`). | DEFAULT | Never share tables. |

## Technical

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-70 | Backend **FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2**, Python 3.12. | DECIDED | ADR-0001. |
| D-71 | Frontend **React + TypeScript + Vite PWA**, mobile-first, one app with role-based areas. | DECIDED | |
| D-72 | Built by **the owner + AI coding agents (Claude Code / Codex)** using this kit. | DECIDED | Enforcement lives in tooling, not prose. |
| D-73 | Hosting **Google Cloud, Mumbai (asia-south1)**; backups copied to Delhi (asia-south2). | DECIDED | Cloud Run, Cloud SQL Postgres, Cloud Storage, Identity Platform. |
| D-74 | **Shared-schema multi-tenancy with Postgres RLS (FORCE)**. | DEFAULT | ADR-0002. |
| D-75 | **Postgres-backed job queue** (Procrastinate); Redis only when caching is proven necessary. | DEFAULT | ADR-0005. |

## v2 Stage 0 (rebuild from the product kit)

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| D-80 | Rebuild allamc from the product kit, starting at Stage 0; archive the v1 repo as reference only. | DECIDED | v1 wrote production code before any user validation; the method puts a prototype and 5 user tests first. |
| D-81 | First segment: AC / RO / appliance service businesses, 2–30 technicians, one city. The product stays category-configurable. | VALIDATE | A narrow first segment makes recruiting, templates and messaging concrete; confirm with the first 5 interviews. |
| D-82 | Core loop: sell AMC → visit scheduled/logged → technician completes on phone → customer gets report → GST invoice. Renewal reminders come immediately after. | DEFAULT | Everything outside this loop waits until Stage 3 (BRIEF out-of-scope list). |
| D-83 | Technical decisions D-70…D-75 are held as DEFAULT and re-confirmed in the technical rounds after Stage 1. | DEFAULT | Stack choices should follow validated UX needs (offline, languages, devices). |
| D-84 | Thin loop uses starter templates only; the no-code builder moves to "next". | DEFAULT | Supersedes the timing of D-10 (not its intent); cuts a large slice from the skeleton. |
| D-85 | Data migration for early partners is assisted by us; the self-serve import wizard moves to "next". | DEFAULT | Supersedes the timing of D-62. |
| D-86 | WhatsApp in the thin loop = one-tap links only (service report, invoice); Cloud API later. | DEFAULT | Supersedes the timing of D-54. |
| D-87 | Re-tag as **VALIDATE** the decisions behind the brief's riskiest assumptions: D-33, D-34, D-35, D-55, D-56, D-61, D-10, D-11 (confirmed or changed by the Stage 1 prototype tests); D-40 (CA review of GST formats); D-54 (current Meta number/coexistence rules); D-83 (technical re-confirmation after Stage 1). | DECIDED | Supersedes the *status* of those entries, not their content. Owner approval 2026-09-23 (stage-gate session). The tags now match BRIEF.md and NOW.md. |
| D-88 | BRIEF.md approved as the Stage 0 frame: core loop (D-82), first segment D-81 (still VALIDATE), six ranked assumptions, out-of-scope list. | DECIDED | Owner approval 2026-09-23 (stage-gate session). |
