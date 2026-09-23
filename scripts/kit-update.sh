#!/usr/bin/env bash
# kit-update.sh (kit-owned) — pull the latest kit-owned files from the kit template repo.
# Usage: bash scripts/kit-update.sh [<kit-git-url>] [<ref, default main>]
# Product-owned files are never touched. Review the diff, run verify.sh, commit "kit: update to vX".
set -euo pipefail
cd "$(dirname "$0")/.."
url="${1:-$(git remote get-url kit 2>/dev/null || true)}"
ref="${2:-main}"
[ -n "$url" ] || { echo "usage: $0 <kit-git-url> [ref]  (or: git remote add kit <url>)"; exit 2; }
git remote get-url kit >/dev/null 2>&1 || git remote add kit "$url"
git fetch --quiet kit "$ref"
files=$(git show "kit/$ref:kit.json" | python -c 'import json,sys;print("\n".join(json.load(sys.stdin)["kit_owned_files"]))' 2>/dev/null \
     || git show "kit/$ref:kit.json" | python3 -c 'import json,sys;print("\n".join(json.load(sys.stdin)["kit_owned_files"]))')
echo "$files" | while IFS= read -r f; do
  [ -n "$f" ] || continue
  git checkout "kit/$ref" -- "$f" 2>/dev/null && echo "updated $f" || echo "skip $f (not in kit)"
done
new_version=$(git show "kit/$ref:KIT_VERSION")
echo "Kit files now at $new_version. Also update kit_version in kit.json, review 'git diff --cached', run verify.sh."
