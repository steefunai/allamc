# scripts/verify.d — product-owned suites

Every `*.sh` here is sourced by `scripts/verify.sh` in name order. Use the helpers `note`, `bad`,
`run` and honour `SKIP_DB` / `CI`. Suggested split (BOOT-001 creates them):

- `10-backend.sh` — lint, types, boundary checks, unit tests; integration tests unless `SKIP_DB=1`
- `20-frontend.sh` — typecheck, lint, unit/component tests, build; e2e unless `SKIP_DB=1`
- `50-invariants.sh` — grep/AST backstops for this product's day-one invariants

Example (`10-backend.sh`):

```bash
if [ -f backend/pyproject.toml ]; then
  run "backend: lint"  bash -c "cd backend && uv run ruff check ."
  run "backend: unit"  bash -c "cd backend && uv run pytest -q -m unit"
  [ "${SKIP_DB:-0}" = "1" ] || run "backend: integration" bash -c "cd backend && uv run pytest -q -m integration"
elif [ "${CI:-false}" = "true" ]; then
  bad "backend not bootstrapped"
fi
```
