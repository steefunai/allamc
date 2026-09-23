#!/usr/bin/env bash
# Claude Code Stop hook: block ending a turn while the fast suite is red (exit 2 feeds stderr back).
input=$(cat)
# One forced retry per stop, so auto mode can't loop forever; pre-commit and CI still gate.
printf '%s' "$input" | grep -qE '"stop_hook_active": *true' && exit 0
# Nothing changed (plans, questions) → nothing to verify.
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then exit 0; fi
out=$(SKIP_DB=1 bash scripts/verify.sh 2>&1) || { printf '%s\n' "$out" | tail -n 60 >&2; exit 2; }
exit 0
