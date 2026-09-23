# AUTHORITY_REQUIRED configuration

Business, tax and security values are **never** hard-coded. They are read at runtime with
`config.require_int / require_bp / require_paise / require_list / require_bool(key)` from `config_value`.
If a key is unset the operation refuses with `ErrorCode.CONFIG_NOT_SET` and the UI shows
"Not set — needed for X" (SCR-SET-03). Tests use the **DEV_TEST** seed (`backend/app/seeds/dev_test_config.py`);
**production starts empty** and an authorised Admin sets each value.

- **Platform scope:** set by allamc.in platform admins; applies to all tenants.
- **Tenant scope:** set by the tenant Owner (`tenant.config.manage`, Owner-only).
- Values that come from law (tax rates, thresholds) must cite their source in the `set` reason.

| Key | Scope | Type | Used by | DEV_TEST seed |
|---|---|---|---|---|
| `tax.allowed_gst_rates_bp` | platform | list[int] | VS-005, VS-007 | `[0, 500, 1800, 4000]` |
| `billing.round_off_enabled` | tenant | bool | VS-007 | `true` |
| `billing.default_payment_terms_days` | tenant | int | VS-007 | `15` |
| `einvoice.turnover_threshold_paise` | platform | paise | VS-035 | `500000000000` |
| `einvoice.enabled` | tenant | bool | VS-035 | `false` |
| `security.otp_max_attempts` | platform | int | VS-001 | `5` |
| `security.lockout_minutes` | platform | int | VS-001 | `15` |
| `security.access_token_ttl_s` | platform | int | VS-001 | `900` |
| `security.refresh_token_ttl_days` | platform | int | VS-001 | `30` |
| `security.otp_send_limit_per_hour` | platform | int | VS-001 | `5` |
| `security.otp_send_limit_per_ip_hour` | platform | int | VS-001 | `20` |
| `security.otp_send_global_per_hour` | platform | int | VS-001 | `1000` |
| `security.login_ticket_ttl_s` | platform | int | VS-001 | `300` |
| `proof.otp_ttl_s` | platform | int | VS-012 | `300` |
| `proof.dispute_window_hours` | tenant | int | VS-013 | `48` |
| `sync.max_clock_skew_minutes` | platform | int | VS-013 | `10` |
| `media.max_photo_kb` | platform | int | VS-012 | `300` |
| `sla.default_response_hours_by_priority` | tenant | map p1/p2/p3→int | VS-011 | `{"p1":4,"p2":24,"p3":72}` |
| `public.request_rate_limit_per_hour` | platform | int | VS-011 | `10` |
| `contracts.pm_due_window_days` | tenant | int | VS-010 | `7` |
| `renewal.default_uplift_bp` | tenant | bp | VS-010 | `500` |
| `renewal.reminder_offsets_days` | tenant | list[int] | VS-010, VS-015 | `[60, 30, 7]` |
| `renewal.lapse_after_days` | tenant | int | VS-016 | `30` |
| `quotes.office_approval_threshold_paise` | tenant | paise | VS-014 | `500000` |
| `quotes.link_ttl_hours` | tenant | int | VS-014 | `72` |
| `links.document_ttl_days` | platform | int | VS-015 | `30` |
| `reporting.upsell_breakdown_threshold` | tenant | int | VS-016 | `3` |
| `reporting.repeat_complaint_days` | tenant | int | VS-016 | `30` |
| `imports.undo_window_days` | platform | int | VS-017 | `7` |
| `imports.max_rows` | platform | int | VS-017 | `20000` |
| `payments.gateway_enabled` | tenant | bool | VS-008 | `false` |
| `amendments.requires_owner_approval` | tenant | bool | VS-018 | `true` |
| `amendments.removal_credit_policy` | tenant | enum prorata/none | VS-018 | `"prorata"` |
| `emandate.max_debit_without_afa_paise` | platform | paise | VS-019 | `1500000` |
| `emandate.pre_debit_notice_hours` | platform | int | VS-019 | `24` |
| `cash.wallet_alert_limit_paise` | tenant | paise | VS-023 | `2000000` |
| `purchasing.po_approval_threshold_paise` | tenant | paise | VS-022 | `2500000` |
| `plans.entitlements` | platform | json | VS-028 | see seed file |
| `support.max_grant_hours` | platform | int | VS-029 | `72` |

DEV_TEST values are **illustrative test fixtures, not legal or business advice**. In particular GST rate
slabs, the e-invoicing threshold and RBI e-mandate limits change over time and must be set in production
from current official sources by an authorised Admin (and confirmed by a CA where tax is involved).
Adding a key: add a row here first, then the seed, then the `require_*` call — never a code default.

Hard caps that come from an ADR rather than business policy are enforced in code on read, not defaulted:
`security.login_ticket_ttl_s` must be ≤ 300 (ADR-0011 D4); a larger stored value refuses with `CONFIG_NOT_SET`.
