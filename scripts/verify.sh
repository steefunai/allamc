#!/usr/bin/env bash
#
# verify.sh (kit-owned) — the hard backstop. Wired into the git pre-commit hook, the agent Stop hook
# and CI. Two parts:
#   1. Product suites: every scripts/verify.d/*.sh (product-owned) is sourced in name order. They use
#      the helpers below (note / bad / run) and the variables SKIP_DB and CI.
#   2. Kit checks: NOW.md header, PROGRESS.md wording, UI gate. Identical in every product.
#
#   SKIP_DB=1  skip DB-backed tiers (local pre-commit / Stop hook only; forbidden in CI)
#
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
note() { printf '\n=== %s ===\n' "$1"; }
bad()  { printf 'VIOLATION: %s\n' "$1"; fail=1; }
run()  { local label="$1"; shift; note "$label"; "$@" || { printf 'FAILED: %s\n' "$label"; fail=1; }; }

# Per-user tools aren't on PATH in non-interactive shells (hooks, CI children, cmd on Windows).
for d in "$HOME/.local/bin" "$HOME/.cargo/bin"; do [ -d "$d" ] && PATH="$d:$PATH"; done
export PATH

# A working Python for the kit checks (the Windows Store 'python3' stub doesn't count).
kitpy() {
  if command -v uv >/dev/null 2>&1; then uv run --no-project --quiet python "$@"
  elif python3 -c '' >/dev/null 2>&1; then python3 "$@"
  elif python -c '' >/dev/null 2>&1; then python "$@"
  else printf 'no Python found for kit checks\n'; return 1; fi
}

if [ "${CI:-false}" = "true" ] && [ "${SKIP_DB:-0}" = "1" ]; then bad "SKIP_DB=1 is not allowed in CI."; fi

# --- 1. product suites -----------------------------------------------------------------------------
shopt -s nullglob
suites=(scripts/verify.d/*.sh)
if [ ${#suites[@]} -eq 0 ]; then
  if [ "${CI:-false}" = "true" ]; then bad "no product suites in scripts/verify.d/ (BOOT-001 adds them)."
  else printf '\n(!) No product suites in scripts/verify.d/ yet — kit checks only.\n'; fi
fi
for suite in "${suites[@]}"; do
  # shellcheck source=/dev/null
  source "$suite"
done

# --- 2. kit checks ---------------------------------------------------------------------------------
note "NOW.md header"
kitpy scripts/check_now.py || bad "NOW.md header invalid (see above)."

note "PROGRESS.md wording"
if [ -f PROGRESS.md ] && grep -nEi '\bcomplete[ds]?\b' PROGRESS.md | grep -v 'backend-complete, UI pending'; then
  bad "PROGRESS.md: statuses are NOT_STARTED / IN_PROGRESS / ACCEPTED / exactly 'backend-complete, UI pending'."
fi

note "UI gate (screens exist for every ACCEPTED slice; UI debt blocks progress)"
kitpy scripts/check_ui_gate.py || bad "UI gate failed (see above)."

note "RESULT"
if [ "$fail" -ne 0 ]; then printf 'verify.sh FAILED — fix the violations above before committing.\n'; exit 1; fi
printf 'verify.sh PASSED.\n'
