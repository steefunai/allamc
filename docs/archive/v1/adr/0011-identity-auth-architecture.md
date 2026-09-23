# ADR-0011 — Identity, sessions and phone-OTP authentication
Status: Accepted (owner-approved VS-001 plan with conditions, 2026-09-23) · Slice: VS-001 · Decision refs:
D-50, D-52, D-70, D-73 · Related: ADR-0002 (RLS), ADR-0006 (offline), ADR-0007 (person), ADR-0010

## Context
Every user signs in with phone OTP; office users may also use email + password. The plan requires OTP
lockout after N attempts and expired/wrong-code errors, cross-tenant isolation, device-bound technician
sessions, refresh-token replay detection, and a global `person` (D-52). Local and CI must not need GCP
credentials.

## Decisions

### D1 — Backend-mediated authentication behind `AuthProviderPort`
- The browser never talks to Firebase/Identity Platform. `POST /api/auth/otp/start` makes the backend call
  Identity Toolkit `accounts:sendVerificationCode`; the provider's `sessionInfo` stays server-side in
  `otp_challenge`. `POST /api/auth/otp/verify` calls `accounts:signInWithPhoneNumber`. Only so can our
  server see every attempt and enforce `security.otp_max_attempts` / `security.lockout_minutes`.
- Email + password: `accounts:signInWithPassword` via the backend. Linking email + password to the phone
  account uses the admin `accounts:update` call.
- `AuthProviderPort` (in `app/ports/auth_provider.py`) has one REST adapter (`identity` module) used against
  the **Firebase Auth emulator** locally and in CI (`AUTH_EMULATOR_HOST`, project `demo-allamc`, no
  credentials) and against **Identity Platform** in OPS-001 (API key, service account for admin calls,
  reCAPTCHA). `FakeAuthProvider` (tests) covers states the emulator cannot produce (expired sessions).
- **Send limits** (all AUTHORITY_REQUIRED): per phone `security.otp_send_limit_per_hour`, per client IP
  `security.otp_send_limit_per_ip_hour` (IP stored only as an HMAC), and a global ceiling
  `security.otp_send_global_per_hour`. Exceeding any → `RATE_LIMITED`. Windows are the rolling last hour.
- **+91 only**, enforced in code (`app/common/phone.py`: `^\+91[6-9]\d{9}$`). Identity Platform's SMS region
  policy must also be India-only (OPS-001 checklist).
- **reCAPTCHA:** in staging/production `otp/start` requires a reCAPTCHA token, passed through to Identity
  Toolkit; `Settings` refuses to start there with the requirement off.
- **Password recovery:** phone OTP is the only path. There is no reset-email flow: a user signs in with OTP
  and sets a new password in the Sign-in methods panel (`PUT /api/me/credentials`), which is only available
  in a session created by phone OTP.

### D2 — Two narrow `SECURITY DEFINER` functions for cross-tenant identity lookups
RLS correctly hides every tenant's rows from `allamc_app`, and platform tables are SELECT-only for it. Login
must still answer "which tenants is this phone a member of?" and must create a `person`. Two owner-owned
functions do exactly that and nothing else:
- `identity_upsert_person(phone_e164 text, auth_uid text) → uuid`: upserts the verified person.
- `identity_memberships(person_id uuid) → (tenant_id, user_id, tenant_name, user_status, display_name)`:
  users **active or invited** in tenants whose status is **not closed**, matched by `app_user.person_id`
  (set with the `person_link` when a membership is activated) or, for invited users not yet linked, by the
  person's phone.
Both: `SET search_path = pg_catalog, public`, `REVOKE EXECUTE … FROM PUBLIC`, `GRANT EXECUTE … TO
allamc_app` only. Tests prove `allamc_app` still sees no rows of `app_user`, `person_link` or other tenants
when it queries the tables directly. The architecture test allowlists exactly these two definer functions.

### D3 — Tokens and sessions
- **Access token:** JWT, HS256, header `kid`, claims `typ=access, sub=user_id, tid, sid, did, exp` (TTL
  `security.access_token_ttl_s`). Signed with the active key of a **key set** (`JWT_KEYS` = JSON
  `{kid: secret}`, `JWT_ACTIVE_KID`); verification accepts any key in the set, so keys rotate by adding a
  new kid, switching the active one, and removing the old one after one refresh-TTL.
- Every request re-checks, inside the request's tenant transaction, that the session is not revoked or
  expired and the user is active, and loads permissions fresh, so disabling a user or revoking a family
  takes effect immediately.
- **Refresh token:** JWT (`typ=refresh, tid, sid, jti`) in an httpOnly, Secure, `SameSite=Strict` cookie
  with `Path=/api/auth`; only the SHA-256 of its `jti` is stored. Each refresh rotates to a new
  `auth_session` row in the same family (`rotated_at`, `replaced_by_id`). Presenting a rotated token revokes
  the whole family → `AUTH_TOKEN_REVOKED`. Refresh/logout also require the header
  `X-Requested-With: allamc` (CSRF defence in depth). TTL `security.refresh_token_ttl_days`.
- **Device binding:** the session stores the client `device_id`; a user holding the Technician role can
  refresh only from that device.
- **For VS-013 (recorded now):** a 401 **never** clears the offline outbox. The client refreshes and
  replays; if refresh fails it asks the user to sign in again and replays afterwards. Commands from a user
  who was disabled meanwhile are not dropped: the server moves them to the conflict queue.
- **Same-origin:** the refresh cookie requires the API on the app's origin under `/api`. All module routers
  are mounted under `/api` (ops probes stay at `/healthz`, `/readyz`). Locally the Vite dev/preview proxy
  forwards `/api`. OPS-001: a Firebase Hosting rewrite `/api/**` → Cloud Run (confirm asia-south1 support),
  otherwise an HTTPS load balancer serving both.

### D4 — Choosing a membership without trusting a client `tenant_id`
A successful OTP/password verification returns a **login ticket** (JWT with `jti`, `sub=person_id`, TTL
`security.login_ticket_ttl_s`, capped at 300 s in code) and the person's memberships. The client picks a
membership by `user_id` (`POST /api/auth/session`); the server derives the tenant from the membership list.
Tickets are **single-use**: the `jti` is stored in `login_ticket` and consumed atomically
(`UPDATE … WHERE used_at IS NULL`); a replay → `AUTH_TOKEN_REVOKED`. A verified phone with no membership
may use its ticket for `POST /api/auth/signup`.
**Invited users:** the first OTP login with the invited phone number **activates the membership** (status
`invited → active`, person linked), audited. Until VS-015 sends invite messages, SCR-ID-03 tells the owner
"Ask them to log in with this phone number".

### D5 — Audit now, through the port (owner condition)
Role, permission, user-status, branch and membership-activation changes call
`AuditPort.append(entry, session)` in the same transaction. Until VS-002 the binding is the BOOT-001 test
double (`tests/doubles/audit.py`); `create_app()` **refuses to start** without a bound AuditPort, so the
only runnable app before VS-002 is the test/dev factory `tests/support/app_factory.py`, which binds the
double. VS-002 binds the real implementation in `app/wiring.py` without touching VS-001 services.
Tests assert the audit entry is appended on the same session inside the business transaction.

### D6 — Scope limits
Tenants get `status='trial'` only; trial end and enforcement are VS-028. The language preference stays
per-device until VS-003. Standard roles only (custom roles are VS-025).

### D7 — Personal data
Phones are stored in `person.phone_e164` / `app_user.phone_e164` as the product requires; rate-limit and
lockout tables store only `HMAC-SHA256(PII_HMAC_KEY, value)`. **Rotating `PII_HMAC_KEY` discards existing
lockouts and rate-limit history** (they no longer match); that is acceptable because both are short-lived.
Logs never contain phones, emails, codes, tickets or tokens.

### D8 — Housekeeping
A Procrastinate periodic task `identity.purge_auth_artifacts` deletes expired `otp_challenge` rows,
used/expired `login_ticket` rows and lapsed `phone_lockout` rows. `otp_challenge.expires_at` = creation +
1 hour, the rate-limit window the per-hour keys are defined over; the provider expires the code itself
sooner.

### D9 — Additional error code
`AUTH_CREDENTIALS_INVALID` (wrong email/password) joins the approved `AUTH_REQUIRED` and `LAST_OWNER`.
Reusing `AUTH_OTP_INVALID` for passwords would mislead users.

### D10 — Authorization rules added after slice review (VS-001)
- **Scope containment (D-50).** An actor without all-branch scope sees and manages only users whose branches
  lie wholly inside the actor's own (others return `NOT_FOUND`, like other tenants' rows), and may grant
  only `branches`/`own` scope over a subset of their own branches (`scope_exceeds_yours`). `own` scope
  carries the person's home branches, so a branch manager can manage their technicians.
- **No self-change.** Nobody changes their own roles or scope or disables themselves (`self_change`); an
  Owner doing so gets the more specific `LAST_OWNER`. The UI shows these refusals up front (Design
  Fitness #3) rather than on click.
- **Password sessions** open only memberships that password sign-in offers (`password_eligible`: active,
  holding a non-technician role); the same predicate guards both steps, and refresh re-checks it, so a
  password session stops once its user becomes technician-only.
- **Races.** Owner demotion/disable counts other active Owners under a per-tenant advisory lock; OTP
  verification runs check-lockout → provider → count-failure under a per-phone advisory lock; a
  concurrent duplicate invite maps the unique violation to `DUPLICATE`. The OTP *send* counters stay
  approximate (TD-015).

## Consequences
- `otp_challenge`, `phone_lockout`, `login_ticket` and `person` are platform tables (no tenant RLS), listed
  in DATA-001 §8 and the architecture test's `PLATFORM_TABLES` with this ADR as reference.
- The frontend has no Firebase SDK in VS-001; OPS-001 adds reCAPTCHA token acquisition for production.
- Integration tests need the emulator (`docker compose up -d`); `verify.sh` preflights it like the DB.
