#!/usr/bin/env bash
# new-product.sh — run once in a repo created from the kit template.
# Usage: bash scripts/new-product.sh <product-slug> <github-owner>
set -euo pipefail
cd "$(dirname "$0")/.."
product="${1:?product slug, e.g. allamc}"; owner="${2:?GitHub username or team for CODEOWNERS}"
today=$(date +%Y-%m-%d)
files=$(grep -rl --exclude-dir=.git --exclude-dir=scripts --exclude-dir=.claude --exclude-dir=.githooks -e '{{PRODUCT}}' -e '{{OWNER}}' . || true)
for f in $files; do
  sed -i.bak -e "s/{{PRODUCT}}/$product/g" -e "s/{{OWNER}}/$owner/g" "$f" && rm -f "$f.bak"
done
sed -i.bak -e "s/^updated: YYYY-MM-DD/updated: $today/" NOW.md && rm -f NOW.md.bak
rm -f .kit-template
chmod +x scripts/*.sh scripts/hooks/*.sh .githooks/pre-commit
git config core.hooksPath .githooks
echo "Product '$product' initialised. Next:"
echo "  1. git remote add kit <kit-template-url>   (for scripts/kit-update.sh)"
echo "     git add -A && git commit -m \"init: $product\" && git push"
echo "     Protect main: Code Owner review now; require the verify check after BOOT-001."
echo "  2. Create a Claude Project '$product' (instructions: README 'Standard project instructions')"
echo "  3. In Claude Code: /frame-product"
