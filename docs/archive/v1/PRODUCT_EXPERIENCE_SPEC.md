# Product Experience Specification & Styling Contract — allamc.in

Defines every screen the plan names (SCR-ids), the navigation per role, the **Styling Contract** (tokens
in `docs/design-tokens.json`) and the **Design Fitness** checks used by the UI gate in
`DEFINITION_OF_DONE.md`. A slice with screens here is not ACCEPTED until those screens ship.

## 1. Experience principles

1. **Phone first, desk second.** Every screen is designed at 360 px first, then expanded at ≥ 768 px
   (tablet) and ≥ 1280 px (desk). Office tables collapse to cards on phones — never horizontal scroll
   for primary content.
2. **Three taps to the job.** The most frequent task per role is reachable from home in ≤ 3 taps
   (log a job, start my next job, record a payment, see expiring contracts).
3. **Calm and legible.** Neutral surfaces, one brand colour, generous spacing; no decorative gradients,
   no stock illustrations in working screens.
4. **Say why, not just no.** Restricted actions are shown disabled with a one-line reason; config that is
   not set shows "Not set — needed for X" with a link for Owners.
5. **Works in a basement.** Technician screens never block on network; sync state is always visible but
   never alarming.
6. **Two languages, one layout.** Hindi strings are ~30% longer; layouts must not truncate primary labels
   in hi.

## 2. Personas

| Persona | Device | Primary jobs |
|---|---|---|
| Owner | Phone + laptop | Renewals, cash, approvals, settings |
| Branch Manager | Laptop | SLA, team, approvals for own branches |
| Dispatcher / office staff | Laptop (+ phone) | Log calls, assign, chase, bill |
| Technician | Budget Android phone, often offline | Today's jobs, checklist, proof, quotes |
| Accountant | Laptop | Invoices, payments, GST exports |
| Storekeeper (MVP-2) | Laptop/tablet | Stock, transfers, GRN |
| Customer contact | Phone | Request service, approve quotes, pay, view reports |

## 3. Navigation by role

- **Phone (< 768 px):** bottom navigation, max 5 items; "More" sheet for the rest.
  - Technician: *My day · Jobs · Sync · Profile*
  - Office roles: *Home · Jobs · Customers · Billing · More*
- **≥ 768 px:** left sidebar with the same information architecture plus Contracts, Catalogue, Reports,
  Settings as permitted; top bar with branch switcher, search (customers by phone/name/GSTIN, jobs by
  number), language toggle, profile.
- Standard role bundles (initial): Owner = all; Branch Manager = all except `*` Owner-only; Dispatcher =
  customers.*, contracts.view, jobs.* except execute, quotes.office_approve, payments.record;
  Technician = jobs.view(own), jobs.execute, quotes.create, payments.record (cash/UPI on job);
  Accountant = billing.*, payments.*, customers.view, reports.view; Storekeeper = inventory.*,
  purchasing.manage.

## 4. Screens

Each screen lists purpose, key content, primary action, and states that must be designed (loading,
empty, error, offline, no-permission). Screens inherit the shell (SCR-SHELL-01).

### Shell & identity
- **SCR-SHELL-01 App shell** — responsive nav, branch switcher, language toggle, offline banner, toast
  region, error boundary with request id.
- **SCR-ID-01 Business sign-up** — business name, owner phone (OTP), state; creates tenant; next: guided
  setup checklist (company profile, first asset type, first customer).
- **SCR-ID-02 Login** — phone OTP (default) or email + password tab; lockout message with time left.
- **SCR-ID-03 Users** — list with role chips and status; invite by phone; disable; role/scope editor
  (standard roles in MVP-1). Invited rows say "Ask them to log in with this phone number" until VS-015.
  *Sign-in methods panel* (VS-001): reached from the profile menu after a phone-OTP login; set email +
  password for office users (`PUT /api/me/credentials`); phone OTP is the only password-recovery path.
- **SCR-ID-04 Branches** — list + form (address, state, optional GSTIN).

### Settings
- **SCR-SET-01 Company profile & GST** — GSTIN with live validation, address, logo, bank/UPI, footer.
- **SCR-SET-02 Number series** — per branch/doc type/FY with live preview of the next number.
- **SCR-SET-03 Business rules** — every tenant AUTHORITY_REQUIRED key grouped (Billing, Service,
  Renewals, Security) with status chip Set/Not set and "used by" explanation.
- **SCR-SET-04 Messages & channels** — channel status (email, WhatsApp link, later Cloud API), template
  list per event × language with preview.

### Catalogue
- **SCR-CAT-01 Asset types** — list + "Start from template" gallery.
- **SCR-CAT-02 Asset type builder** — field list with add/reorder (drag + buttons), live form preview
  (phone frame), bilingual labels, Publish with version note.
- **SCR-CAT-03 Checklist builder** — per job kind; step editor; live technician preview.
- **SCR-CAT-04 Version history** — versions with published date and usage counts.
- **SCR-CAT-05 Parts & services** — searchable list, category filter, CSV export.
- **SCR-CAT-06 Part / service editor** — HSN/SAC, GST rate picker (allowed rates only), price, tracking.

### Customers
- **SCR-CUS-01 Customers** — one search box; cards on phone, table on desk; quick "New job" per row.
- **SCR-CUS-02 Customer detail** — header (name, primary phone tap-to-call, GSTIN), tabs: Sites &
  assets · Contracts · Jobs · Invoices & ledger · Contacts.
- **SCR-CUS-03 Asset detail** — attributes (from pinned version), coverage status chip, timeline of jobs
  and contracts, QR preview/regenerate.
- **SCR-CUS-04 QR sticker sheet** — select assets → A4 PDF preview → download/print.

### Contracts
- **SCR-CON-01 Contract types** — list; start from template.
- **SCR-CON-02 Coverage rules editor** — grouped toggles and amounts; plain-language summary
  ("Labour covered. Parts covered except gas and filters, up to ₹5,000 per AC per year…").
- **SCR-CON-03 Contracts** — filters: status, expiring in 30/60/90, branch, type; totals row.
- **SCR-CON-04 New contract wizard** — steps with progress; review step shows invoice preview with GST.
- **SCR-CON-05 Contract detail** — assets, PM schedule, usage vs caps, invoices, renewal panel.
- **SCR-CON-06 Renewal quote** — uplift, edits, PDF preview, send (via SCR-SET-04 channels).

### Jobs & dispatch
- **SCR-JOB-01 Dispatch board** — columns by status on desk, segmented list on phone; SLA risk chip;
  bulk assign on desk.
- **SCR-JOB-02 New job** — phone lookup first; asset picker with coverage chip; duplicate warning
  inline.
- **SCR-JOB-03 Job detail (office)** — timeline, checklist results, media, proof, quote, invoice.
- **SCR-JOB-04 Assign sheet** — ranked technicians with reasons ("AC skill · 3 km · 2 jobs today").
- **SCR-JOB-05 Conflict queue** — each conflict shows server vs device values; actions keep server /
  apply device / merge notes.
- **SCR-JOB-06 Approval inbox** — flow-B quotes awaiting office approval.

### Technician (PWA)
- **SCR-TEC-01 My day** — ordered job cards: time, customer, area, asset, SLA chip; call and navigate
  buttons; sync chip in header.
- **SCR-TEC-02 Job execution** — check-in, stepper through checklist (one step per screen on phone),
  large targets, camera/voice buttons, reading inputs with unit.
- **SCR-TEC-03 Close job** — summary, proof method (OTP or signature pad), check-out.
- **SCR-TEC-04 Service report preview** — rendered report, language of customer.
- **SCR-TEC-05 Sync & outbox** — pending commands and uploads with plain-language states; retry.
- **SCR-TEC-06 Quote builder** — search price list, covered vs billable lines with reasons, send for
  approval / capture signature offline.

### Public (no login, tenant-branded)
- **SCR-PUB-01 QR service request** — asset shown, phone OTP, issue text + optional photo, ticket number.
- **SCR-PUB-02 Quote approval** — quote with lines and GST, approve/decline with OTP.
- **SCR-PUB-03 Document view** — service report / invoice via expiring link (payment button when
  applicable).

### Billing
- **SCR-BIL-01 Invoices** — list with status chips, filters, GST exports action.
- **SCR-BIL-02 Invoice detail** — PDF preview, payments, credit notes, share.
- **SCR-BIL-03 New invoice** — line editor with live tax split.
- **SCR-BIL-04 Credit/debit note** — against invoice, remaining value shown.
- **SCR-BIL-05 Record payment** — method, amount, allocation suggestions (oldest first).
- **SCR-BIL-06 Receivables ageing** — buckets, drill to customer.
- **SCR-BIL-07 Customer ledger** — running balance, download.

### Reporting & imports
- **SCR-REP-01 Owner home** — cards in priority order (D-56): Renewals pipeline (30/60/90 value,
  renewal rate trend, lost reasons, upsell flags) → SLA (breaching/at-risk, median response/resolution,
  repeat complaints) → later cards (productivity, receivables & cash) in MVP-2.
- **SCR-IMP-01 Import wizard** — upload → entity set → mapping → validation preview (errors per row) →
  dry run summary → commit.
- **SCR-IMP-02 Import history** — batches with counts and undo (deadline shown).

MVP-2 and later screens are specified in the slice's detailing step (PLAN-GATE rule) and appended here
before the slice starts.

## 5. Styling Contract

The single source of design values is **`docs/design-tokens.json`**; Tailwind's theme is generated from
it in BOOT-001. Components may not use raw hex colours, arbitrary pixel values or other design systems.

- **Colour:** neutral surfaces; one brand colour (`primary`, deep teal) for primary actions and focus;
  semantic colours only for status. Light and dark themes; contrast ≥ 4.5:1 for text.
- **Type:** Inter for Latin, Noto Sans Devanagari for Hindi, system fallback. Base 16 px on phone
  (never below 14 px for any text a technician reads), line-height 1.5.
- **Spacing:** 4 px base scale; comfortable density — list rows ≥ 56 px on phone, 48 px on desk.
- **Shape:** radii sm 6 / md 10 / lg 14; cards with 1 px border and at most `shadow.sm`.
- **Motion:** 150–200 ms ease-out; respect `prefers-reduced-motion`.
- **Icons:** one icon set (Lucide), 20/24 px, always paired with a label for status and primary actions.
- **Component kit:** built in `src/shared/ui/` on Radix primitives (headless, accessible); no
  second component library.

## 6. Design Fitness checks (UI gate)

1. **Status = icon + label**, never colour alone (chips for job, contract, invoice, sync, config).
2. **No decorative gradients**, no background images in working screens.
3. **Restricted actions shown disabled with reason** (tooltip on desk, inline text on phone), not hidden.
4. **Comfortable density:** row heights and targets per §5; technician targets ≥ 48 px.
5. **Alignment:** numbers right-aligned in tables with tabular figures; money via `formatPaise()` with
   ₹ and Indian grouping; form labels above fields on phone, aligned column on desk.
6. **Responsive:** renders without horizontal page scroll at 360 px and uses space well at 1280 px.
7. **i18n:** no literal strings; en and hi complete; no truncated primary labels in hi.
8. **States designed:** loading (skeletons), empty (guided next step), error (message key + retry +
   request id), offline, no-permission.
9. **Accessible:** keyboard reachable, visible focus ring (`primary`), labels for inputs, drag has button
   alternative, axe check clean in the component test.
10. **Tokens only:** lint rule forbids raw hex, arbitrary Tailwind values and inline styles for colour or
    spacing.
