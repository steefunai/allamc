# Product kit (KIT_README) — build products with coding agents without compromising quality

A GitHub **template repository**. Every product starts from it, so every product gets the same
process, guardrails and progress header. Methodology: `docs/PROCESS.md`.

## Start a new product
1. On GitHub: **Use this template** → new repo. Clone it.
2. `bash scripts/new-product.sh <product-slug> <github-owner>` (fills placeholders, enables the git hook).
3. `git remote add kit <this-template-repo-url>` so `scripts/kit-update.sh` can pull kit improvements.
4. First commit: `git add -A && git commit -m "init: <product>" && git push` (`commit -am` misses new files).
   Then protect `main`: check that GitHub recognises the root `CODEOWNERS` file and that the named owner can
   review, and require **Code Owner review**. Require the `verify` check only **after BOOT-001** adds the
   product suite to `scripts/verify.d/` — until then the kit's CI deliberately fails.
5. Create a **Claude Project** named after the product. Knowledge: `docs/BRIEF.md`,
   `docs/PRODUCT_DECISIONS.md`, `docs/requirements.md`, `NOW.md` (re-upload after each weekly review).
   Instructions: the block below.
6. In Claude Code: `/frame-product`. BOOT-001 later adds the stack suites to `scripts/verify.d/` and fills
   CLAUDE.md §1–2 with the product's concrete boundaries and invariants.

### Standard project instructions (paste into each Claude Project)
```
You are the product architect for <PRODUCT>. Follow the methodology in PROCESS.md (the product-builder
skill): two loops (build the right thing / build the thing right), stages with exit gates, vertical
slices with UI, requirements traced FB → REQ → D → VS → SCR/tests, hardening by stability × cost of
failure. The repo documents in project knowledge are the source of truth; chat history is not.
Read NOW.md before advising. Tag new decisions DECIDED / DEFAULT / VALIDATE. Never propose horizontal
slices. End every answer with what the owner must do next.
```

## What the kit owns vs the product
- **Kit-owned** (listed in `kit.json` → `kit_owned_files`): process, quiz bank, verify core, UI gate, NOW
  checker, hooks, commands, reviewer. Update them only via `scripts/kit-update.sh`. `README.md` is the product's own.
- **Product-owned:** brief, decisions, requirements, plan, data contract, experience spec, screen registry
  contents, `scripts/verify.d/*`, CLAUDE.md/AGENTS.md details, all code.
- Document paths live in `kit.json`, so an existing product can keep its own file names.

## Commands
`/frame-product` (Stage 0) · `/build-slice <id>` · `/propose-slices [n]` · `/weekly-review` · `/stage-gate`

## Guardrails on the guardrails
Agents are denied edits to kit-owned files in `.claude/settings.json`; CODEOWNERS requires your review;
the Stop hook (`scripts/hooks/stop-verify.sh`) blocks a turn from ending while the fast suite is red.
Confirm the hooks and permission-rule syntax against the current Claude Code docs when you adopt a new
version.

## Improving the kit
Change it here, bump `KIT_VERSION` (semver) and describe the change in `CHANGELOG.md`; then in each
product run `bash scripts/kit-update.sh`, review, verify, commit `kit: update to vX.Y.Z`.
