# DATA-001 — allamc.in Data Contract

Authoritative for schema, enums, state machines, invariants, error codes and permission codes. Tables are
listed per owning module; **only the owning module reads or writes its tables** (other modules use
ports; `reporting` uses read-only views, ADR-0009). MVP-2+ tables are marked and are binding in shape but
may be refined in their slice with an ADR.

## 1. Conventions

- **Keys:** `id uuid` generated app-side as UUIDv7 (sortable). Human-facing numbers (`JOB-000123`,
  invoice numbers) are separate columns.
- **Tenancy:** every tenant-owned table has `tenant_id uuid NOT NULL` with FK to `tenant`, a composite
  index leading with `tenant_id`, `ENABLE` + `FORCE ROW LEVEL SECURITY`, and policy
  `USING (tenant_id = app_current_tenant()) WITH CHECK (tenant_id = app_current_tenant())`.
  `app_current_tenant()` reads `current_setting('app.tenant_id', true)::uuid` and returns NULL when unset
  (so an unset context sees nothing). Platform-scope tables are listed in §8 and allowlisted in the
  architecture test.
- **Timestamps:** `created_at`, `updated_at` (`timestamptz`, UTC); `created_by uuid` (user or NULL for
  system). Business dates (contract start/end, invoice date) are `date` interpreted in IST.
- **Versioned rows:** `version int NOT NULL DEFAULT 1`, mapped with SQLAlchemy `version_id_col`.
- **Money:** `*_paise bigint`. **Rates:** `*_bp int` (basis points). **Quantities:** `qty_milli bigint`
  (1 unit = 1000). No `float`, `real`, `double precision` or `numeric` money columns anywhere.
- **Soft state:** nothing is hard-deleted except drafts; business records move to terminal statuses.
- **Enums:** Postgres `text` + `CHECK` constraint (easier forward migrations than native enums); the
  Python `StrEnum` in the owning module is the source of truth and a test asserts they match.
- **JSONB:** used only for tenant-defined shapes (asset attributes, checklist steps/results, coverage
  rules, import mappings), always validated by a versioned JSON schema in code.

## 2. Tables by module (MVP-1 unless marked)

### identity
| Table | Key columns |
|---|---|
| `tenant` *(RLS: `id = app_current_tenant()`)* | `id, legal_name, trade_name, status (trial/active/suspended/closed), created_at` |
| `branch` | `tenant_id, id, name, address jsonb, state_code char(2), gstin null, is_default, version` |
| `app_user` | `tenant_id, id, person_id null (set on activation), display_name, phone_e164, email null, auth_uid null, status (invited/active/disabled), preferred_lang (en/hi), skill_tags text[], version` *(VS-001: `person_id`/`auth_uid` nullable until the invited user first logs in; `version` for concurrent edits, ADR-0011)* |
| `role` | `tenant_id, id, code, name, is_system bool, template_code null, owner_only_guard bool` |
| `role_permission` | `tenant_id, role_id, permission_code` (§7) |
| `user_role` | `tenant_id, user_id, role_id, scope (all_branches/branches/own), branch_ids uuid[]` |
| `auth_session` | `tenant_id, id, user_id, refresh_family_id, device_id null, auth_method (otp/password), refresh_jti_hash, expires_at, revoked_at null, rotated_at null, replaced_by_id null, created_at` *(VS-001: rotation + replay detection, ADR-0011 D3)* |
| `person` *(platform)* | `id, phone_e164 unique, auth_uid unique null (identity-provider uid), verified_at` *(written only via `identity_upsert_person()`, ADR-0011 D2)* |
| `person_link` | `tenant_id, person_id, subject_type (user/customer_contact), subject_id, consent_id null` |
| `consent_record` *(platform)* | `id, person_id, purpose, granted_at, withdrawn_at, evidence jsonb` *(created in T3)* |
| `otp_challenge` *(platform, VS-001)* | `id, phone_hmac, ip_hmac, provider_session, failed_attempts, created_at, expires_at, consumed_at null` — HMACs only, never raw phone/IP (ADR-0011 D1, D7) |
| `phone_lockout` *(platform, VS-001)* | `phone_hmac (PK), locked_until` |
| `login_ticket` *(platform, VS-001)* | `jti (PK), person_id, expires_at, used_at null` — single-use (ADR-0011 D4) |

### audit
| `audit_entry` | `tenant_id, id bigint identity, occurred_at, actor_type (user/system/support/customer), actor_id, action, entity_type, entity_id, before jsonb, after jsonb, reason null, request_id` — **append-only trigger** |

### settings
| Table | Key columns |
|---|---|
| `tenant_profile` | `tenant_id (PK), gstin, registered_state_code, address jsonb, logo_key, bank_details jsonb, upi_vpa, invoice_footer, round_off_enabled, version` |
| `config_value` *(scope platform or tenant; RLS allows platform rows read-only)* | `id, scope (platform/tenant), tenant_id null, key, value jsonb, set_by, set_at, version` unique `(scope, tenant_id, key)` |
| `number_series` | `tenant_id, id, branch_id, doc_type (invoice/credit_note/debit_note/receipt_voucher/quote/job/contract/po), fy (e.g. 2026-27), prefix, pad_width, next_value` |

### catalogue
| Table | Key columns |
|---|---|
| `starter_template` *(platform)* | `id, kind (asset_type/checklist/contract_type), code, payload jsonb, version_no` |
| `asset_type` | `tenant_id, id, name, category, status (active/archived), current_version_id` |
| `asset_type_version` | `tenant_id, id, asset_type_id, version_no, field_schema jsonb, status (draft/published), published_at` — **immutable once published (trigger)** |
| `checklist_template` | `tenant_id, id, asset_type_id, job_kind (pm/breakdown/installation/inspection), name, current_version_id` |
| `checklist_version` | `tenant_id, id, template_id, version_no, steps jsonb, status (draft/published), published_at` — immutable once published |
| `part_category` | `tenant_id, id, name, is_consumable` |
| `part` | `tenant_id, id, sku, name, part_category_id, hsn_code, gst_rate_bp, unit, sale_price_paise, tracking (none/batch/serial), status, version` |
| `service_item` | `tenant_id, id, code, name, sac_code, gst_rate_bp, price_paise, status, version` |

### customers
| Table | Key columns |
|---|---|
| `customer` | `tenant_id, id, kind (individual/business), name, gstin null, billing_address jsonb, state_code, default_branch_id, status (active/inactive), version` |
| `customer_contact` | `tenant_id, id, customer_id, name, phone_e164, email null, is_primary, person_id null` unique `(tenant_id, customer_id, phone_e164)` |
| `site` | `tenant_id, id, customer_id, name, address jsonb, state_code, geo_lat_e6 int null, geo_lng_e6 int null` |
| `asset` | `tenant_id, id, customer_id, site_id, asset_type_id, asset_type_version_id, label, attributes jsonb, brand, model, serial_no, install_date, oem_warranty_until, status (active/pending_inspection/scrapped), qr_token unique, version` |

(Coordinates stored as integer micro-degrees to keep the "no float" rule absolute.)

### contracts
| Table | Key columns |
|---|---|
| `contract_type` | `tenant_id, id, name, template_code null, status, current_coverage_version_id` |
| `coverage_version` | `tenant_id, id, contract_type_id, version_no, rules jsonb (schema §6), status (draft/published)` — immutable once published |
| `contract` | `tenant_id, id, number, customer_id, branch_id, contract_type_id, coverage_version_id, start_date, end_date, status, billing_plan (upfront/quarterly/monthly), renewal_mode (reminder/auto_quote/emandate), total_price_paise, renewed_from_id null, lapse_reason null, version` |
| `contract_asset` | `tenant_id, id, contract_id, asset_id, covered_from, covered_to, price_paise, status (active/pending_inspection/removed), version` |
| `pm_schedule_item` | `tenant_id, id, contract_id, asset_id, due_date, window_start, window_end, job_id null, status (planned/generated/done/missed)` |
| `coverage_usage` | `tenant_id, contract_asset_id, coverage_year_start, parts_consumed_paise, breakdown_calls_used, pm_visits_done, version` |
| `amendment` *(MVP-2)* | `tenant_id, id, contract_id, from_version, changes jsonb, status (draft/pending_approval/approved/rejected/applied), prorata_paise, version` |

### jobs
| Table | Key columns |
|---|---|
| `job` | `tenant_id, id, number, kind (pm/breakdown/installation/inspection/revisit), source (office/qr/pm_schedule/portal/whatsapp/import), customer_id, site_id, asset_id null, contract_id null, priority (p1/p2/p3), status (§4.2), assigned_user_id null, scheduled_for null, sla_due_at null, checklist_version_id null, parent_job_id null, description, version` |
| `job_note` | `tenant_id, id, job_id, author_type, author_id, body, source` |
| `job_visit` | `tenant_id, id, job_id, user_id, check_in_at, check_in_lat_e6, check_in_lng_e6, check_in_accuracy_m, check_out_at, …` |
| `job_checklist_result` | `tenant_id, job_id, step_key, value jsonb, media_ids uuid[]` |
| `job_media` | `tenant_id, id, job_id, kind (photo/signature/voice), storage_key, sha256, bytes, captured_at, op_id` |
| `job_proof` | `tenant_id, job_id, method (otp/signature), verified_at null, dispute_until null, disputed_at null` |
| `quote` | `tenant_id, id, number, job_id, flow (A/B/C), status (§4.4), approved_via (otp/link/signature_offline) null, approved_at, subtotal_paise, tax_paise, total_paise, supersedes_id null, version` |
| `quote_line` | `tenant_id, id, quote_id, item_type (part/service), item_id, description, qty_milli, unit_price_paise, gst_rate_bp, covered bool, coverage_reason null` |
| `sync_conflict` | `tenant_id, id, op_id, entity_type, entity_id, server_version, client_payload jsonb, status (open/resolved), resolution null, resolved_by` |

### common (owned by `app/common`, one table)
| `processed_command` | `tenant_id, op_id (PK with tenant_id), user_id, command_type, received_at, result jsonb` |

### billing
| Table | Key columns |
|---|---|
| `invoice` | `tenant_id, id, branch_id, series_id, number null, fy, doc_type (tax_invoice/bill_of_supply), status (§4.3), customer_id, customer_name_snapshot, customer_gstin_snapshot null, place_of_supply_state, supply_type (intra/inter), issue_date, due_date, source_type (contract/job/manual/amendment/import), source_id null, subtotal_paise, cgst_paise, sgst_paise, igst_paise, round_off_paise, total_paise, paid_paise, tds_paise, balance_paise, pdf_key, version` |
| `invoice_line` | `tenant_id, id, invoice_id, description, sac_or_hsn, qty_milli, unit_price_paise, discount_paise, taxable_paise, gst_rate_bp, cgst_paise, sgst_paise, igst_paise, line_total_paise` |
| `credit_note` / `debit_note` | same shape as invoice + `against_invoice_id`, `reason` |
| `receipt_voucher` | `tenant_id, id, number, customer_id, amount_paise, tax_paise, adjusted_paise, status` |
| `payment` | `tenant_id, id, customer_id, method (gateway_link/upi/cash/bank_transfer/cheque), amount_paise, received_on, reference, collected_by_user_id null, gateway_ref null, status (pending/confirmed/failed/reversed), reversal_reason null, version` |
| `payment_allocation` | `tenant_id, id, payment_id, target_type (invoice/receipt_voucher), target_id, amount_paise` |
| `gateway_event` | `tenant_id, provider, event_id unique per provider, received_at, payload_hash, processed_at` |
| `cash_handover` *(MVP-2)* | `tenant_id, id, technician_id, amount_paise, received_by, status, version` |
| `tds_entry` *(MVP-2)* | `tenant_id, id, invoice_id, section, amount_paise, certificate_ref null, status` |

### inventory *(MVP-2)*
| `stock_location` | `tenant_id, id, kind (store/van/in_transit/defective/returned_oem), branch_id, user_id null, name` |
| `stock_movement` *(append-only)* | `tenant_id, id, part_id, from_location_id null, to_location_id null, qty_milli, unit_cost_paise, reason (grn/transfer/consume/return/adjust/defective_in/rma_out), ref_type, ref_id, serial_no null, op_id null` |
| `stock_level` | `tenant_id, location_id, part_id, qty_milli, avg_cost_paise, version` — CHECK `qty_milli >= 0` |
| `serial_unit` | `tenant_id, id, part_id, serial_no, status (in_stock/fitted/defective/returned/scrapped), location_id null, asset_id null, version` |

### purchasing *(MVP-2)*
`supplier`, `purchase_order` (+`po_line`; status draft/pending_approval/approved/partially_received/received/closed/cancelled), `goods_receipt` (+`grn_line`), `vendor_bill` (+`vendor_bill_line`; ITC fields `itc_eligible`, tax paise split).

### notifications
| `channel_config` | `tenant_id, channel (email/wa_link/wa_cloud/sms), status, secret_ref null, sender_meta jsonb` |
| `message_template` | `tenant_id null (null = platform default), event_code, lang, channel, body, provider_template_id null, approval_status` |
| `outbound_message` | `tenant_id, id, event_code, channel, recipient_ref (contact id, never raw phone), status (queued/sent/delivered/failed/manual_link), dedupe_key unique, ref_type, ref_id` |

### imports
| `import_batch` | `tenant_id, id, entity_set, file_key, mapping jsonb, status (§4.6), counts jsonb, committed_at, revert_deadline, reverted_at` |
| `import_row` | `tenant_id, batch_id, row_no, status (valid/invalid/committed/reverted), errors jsonb, created_refs jsonb` |

### platform *(MVP-2 except `plan` seed)*
`plan` *(platform)*: `code, name, entitlements jsonb, status`; `subscription`: `tenant_id, plan_code, status (trial/active/past_due/cancelled/free), seats_technician, period_end, gateway_sub_id`; `support_access_grant`: `tenant_id, id, staff_id, granted_by, reason, expires_at, revoked_at`.

## 3. Enumerations
The allowed values are exactly those listed in parentheses in §2. Adding a value requires a migration
and a DATA-001 amendment (ADR if it changes a state machine).

## 4. State machines
Transitions not listed are forbidden and return `INVALID_STATE_TRANSITION`.

### 4.1 Contract
`draft → active` (≥1 asset; first invoice issued in same transaction) · `draft → cancelled` ·
`active → expired` (system, day after `end_date`) · `active → cancelled` (Owner permission, reason,
credit note per policy) · renewal creates a **new** `draft` with `renewed_from_id`; when an expired
contract has no renewal after `renewal.lapse_after_days`, `lapse_reason` is requested in the dashboard.

### 4.2 Job
`new → assigned` · `assigned → new` (unassign) · `assigned → in_progress` (check-in) ·
`in_progress → awaiting_approval` (quote sent, flows A/B) · `awaiting_approval → in_progress`
(approved) · `awaiting_approval → repair_declined` (terminal, with acknowledgement) ·
`in_progress → completed_on_device` (offline close) · `in_progress → completed` (online proof) ·
`completed_on_device → completed` (sync verified) · `completed → closed` (office review / invoice issued
if billable) · `in_progress → revisit_needed` (creates child job; terminal for parent) ·
`new|assigned → cancelled` (reason).

### 4.3 Invoice / credit note
`draft → issued` (number allocated; immutable after) · `issued → partially_paid → paid` (derived from
allocations + TDS) · `issued|partially_paid → cancelled` only by a full-value credit note. Drafts may be
deleted.

### 4.4 Quote
`draft → sent` · `draft → pending_office` (flow B above threshold) · `pending_office → sent | rejected` ·
`sent → approved | declined | expired` · editing an approved quote creates a new quote with
`supersedes_id`.

### 4.5 Payment
`pending → confirmed | failed` · `confirmed → reversed` (reason; allocations reversed in same
transaction).

### 4.6 Import batch
`uploaded → mapped → validated → committed → reverted` · `validated → discarded` · revert allowed only
before `revert_deadline` and when no dependent records exist.

### 4.7 Catalogue / coverage versions
`draft → published` (immutable). The parent's `current_version_id` moves to the newest published version;
existing assets/contracts/jobs keep their pinned version.

## 5. Invariants

| ID | Invariant | Enforced by |
|---|---|---|
| INV-01 | Every tenant-owned table has `tenant_id` + FORCE RLS; runtime role is `allamc_app` (NOBYPASSRLS, not owner). | Migration convention + architecture test + startup check |
| INV-02 | `tenant_id` is never taken from client input. | Request schemas have no `tenant_id`; review |
| INV-03 | Audit entry written in the same transaction as the change it records. | `AuditPort.append(entry, session)` signature + verify.sh grep + tests |
| INV-04 | `audit_entry` is append-only. | DB trigger |
| INV-05 | Versioned rows change only with a matching `version`. | `version_id_col`; verify.sh grep for bulk updates |
| INV-06 | Money is integer paise, rates integer bp, quantities integer milli. | Column types + Pydantic `StrictInt` + verify.sh greps |
| INV-07 | Line tax = half-up rounding of `taxable_paise × rate_bp / 10000`, split CGST/SGST by halving with the odd paisa assigned to CGST; invoice totals are sums of lines (+ optional round-off line). | `money.py` + table tests (CA to confirm, D-40) |
| INV-08 | Issued documents are immutable; numbers gapless per `number_series`. | Status CHECK + trigger; numbers allocated with `SELECT … FOR UPDATE` on the series row **inside** the issuing transaction (pessimistic lock by design; `number_series` is excluded from optimistic locking) |
| INV-09 | Published catalogue/coverage versions are immutable. | DB trigger |
| INV-10 | Field commands are idempotent by `(tenant_id, op_id)`. | `processed_command` PK, same transaction |
| INV-11 | `stock_level.qty_milli >= 0`; levels change only with a movement row in the same transaction. | CHECK + service rule + test |
| INV-12 | A serial unit is in exactly one place (location or asset). | CHECK (`location_id IS NULL) <> (asset_id IS NULL)` when status requires |
| INV-13 | An asset has at most one active contract per contract type over any date range. | Exclusion constraint on `(asset_id, contract_type_id, daterange)` via `contract_asset` |
| INV-14 | AUTHORITY_REQUIRED keys are never defaulted in code; unset → `CONFIG_NOT_SET`. | `config.require_*` + verify.sh grep |
| INV-15 | Personal data is never logged; outbound messages reference contacts, not raw phones. | Logging filter + review |
| INV-16 | Gateway webhooks processed at most once per `(provider, event_id)`. | Unique constraint |
| INV-17 | Proof of service (OTP/signature/GPS) is immutable once recorded. | No update route + audit |

## 6. JSON schemas (versioned in code under `app/modules/<m>/schemas/`)

- **Asset field schema:** `{fields: [{key, type, label: {en, hi}, required, options?, unit?, decimals?}]}`;
  numeric values stored as integers with `decimals` scaling.
- **Checklist steps:** `{steps: [{key, type (check/reading/photo/note/select), label: {en, hi}, required,
  photo_required, min?, max?, unit?, options?}]}`.
- **Coverage rules:** `{labour_covered, covered_part_category_ids[], excluded_part_category_ids[],
  consumables_covered, parts_cap_paise_per_asset_year|null, pm_visits_per_year,
  breakdown_calls_per_year|null, response_sla_hours {p1,p2,p3}, out_of_coverage_flow (A/B/C),
  proof {otp_when_online, signature_when_offline, gps_check_in, photos_per_checklist}}`.

## 7. Permission codes (roles are bundles; scope applies to branch-owned data)

`tenant.settings.manage`* · `tenant.config.manage`* · `tenant.series.manage`* · `users.manage` ·
`roles.manage`* · `branches.manage` · `catalogue.manage` · `pricing.manage` · `customers.view` ·
`customers.manage` · `contracts.view` · `contracts.manage` · `contracts.activate` · `contracts.cancel`* ·
`jobs.view` · `jobs.create` · `jobs.assign` · `jobs.execute` · `jobs.resolve_conflicts` ·
`quotes.create` · `quotes.free_price` · `quotes.office_approve` · `billing.view` · `billing.issue` ·
`billing.credit_note` · `payments.record` · `payments.reverse` · `inventory.view` · `inventory.move` ·
`inventory.adjust` · `purchasing.manage` · `purchasing.approve` · `reports.view` · `imports.run` ·
`audit.view` · `support.grant`*

`*` = Owner-only guard: cannot be added to custom roles. Standard role bundles are seeded from
`app/modules/identity/role_templates.py` and listed in the Product Experience Spec §3.

## 8. Platform-scope tables (no tenant RLS; allowlisted)
`person`, `consent_record`, `starter_template`, `plan`, `otp_challenge`, `phone_lockout`, `login_ticket`
(VS-001, ADR-0011), and platform rows of `config_value`. Tenants
read these only through module APIs; `allamc_app` has SELECT-only on them except via platform-admin
endpoints guarded by staff auth.

## 9. Error codes (initial `ErrorCode` enum; add here first, then in code)

`AUTH_OTP_INVALID` · `AUTH_OTP_EXPIRED` · `AUTH_LOCKED` · `AUTH_TOKEN_REVOKED` · `PERMISSION_DENIED` ·
`NOT_FOUND` · `VALIDATION_FAILED` · `VERSION_CONFLICT` · `INVALID_STATE_TRANSITION` · `CONFIG_NOT_SET` ·
`DUPLICATE` · `RATE_LIMITED` · `GSTIN_INVALID` · `TAX_RATE_NOT_ALLOWED` · `PLACE_OF_SUPPLY_REQUIRED` ·
`DOCUMENT_IMMUTABLE` · `CREDIT_EXCEEDS_BALANCE` · `OVER_ALLOCATION` · `CONTRACT_NO_ASSETS` ·
`CONTRACT_OVERLAP` · `VERSION_PUBLISHED_IMMUTABLE` · `PROOF_REQUIRED` · `QUOTE_LINK_INVALID` ·
`SYNC_STALE_COMMAND` · `IMPORT_REVERT_BLOCKED` · `WEBHOOK_SIGNATURE_INVALID` · `STOCK_INSUFFICIENT`
(MVP-2) · `ENTITLEMENT_EXCEEDED` (MVP-2) · `AUTH_REQUIRED` (VS-001: missing/expired access token) · `LAST_OWNER` (VS-001: would leave the tenant
without an active Owner, or an Owner disabling/demoting themselves) · `AUTH_CREDENTIALS_INVALID` (VS-001:
wrong email/password) · `INTERNAL_ERROR` (BOOT-001: unhandled failure; the envelope
still carries `request_id`, never exception text)
