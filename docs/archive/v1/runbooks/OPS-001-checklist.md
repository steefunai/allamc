# OPS-001 checklist — items accumulated by earlier slices

Each item names the slice/ADR that raised it. OPS-001 is not ACCEPTED until every box is ticked or moved to
TECH_DEBT with a reason.

## Identity & auth (VS-001, ADR-0011)
- [ ] Identity Platform enabled on the prod/staging projects with **phone** and **email/password** providers.
- [ ] **SMS region policy: allow India only** (matches the +91-only rule enforced in code).
- [ ] reCAPTCHA (Enterprise) configured for phone auth; the frontend obtains a token for `otp/start`;
      `AUTH_REQUIRE_RECAPTCHA` is on (settings refuse staging/prod without it).
- [ ] Service account for the admin `accounts:update` call (Sign-in methods panel), via Workload Identity;
      API key in Secret Manager. Wire `IdentityToolkitAuthProvider` with the real base URL, no emulator.
- [ ] `JWT_KEYS` / `JWT_ACTIVE_KID` and `PII_HMAC_KEY` in Secret Manager; rotation runbook (add kid →
      switch active → remove old after `security.refresh_token_ttl_days`). Rotating `PII_HMAC_KEY`
      discards lockouts/rate-limit history (accepted).
- [ ] **Same-origin API:** Firebase Hosting rewrite `/api/**` → Cloud Run `api` (confirm the rewrite is
      supported for asia-south1); otherwise an HTTPS load balancer serving the SPA and `/api` together.
      The refresh cookie (`Path=/api/auth`, `SameSite=Strict`) depends on this.
- [ ] Client IP for per-IP OTP limits: run uvicorn with `--proxy-headers` and trust only the platform's
      forwarding hops, so `X-Forwarded-For` can't be spoofed.
- [ ] Production `create_app()` needs a bound AuditPort (VS-002) — deploys before VS-002 cannot start by design.
- [ ] Procrastinate worker scheduled task `identity.purge_auth_artifacts` running.

## Carried from BOOT-001
- [ ] Strict CSP header in Firebase Hosting (TD-006).
- [ ] Lighthouse CI against staging, LCP ≤ 2.5 s for `/app` and `/tech` (TD-007).
