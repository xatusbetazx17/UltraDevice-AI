#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-UltraDevice-AI_pro.zip}"
REPO="${2:-https://github.com/xatusbetazx17/UltraDevice-AI.git}"
BRANCH="${3:-import/v0-2}"

tmp=$(mktemp -d)
unzip -q "$ZIP" -d "$tmp"
src_dir=$(find "$tmp" -maxdepth 2 -type d -name "UltraDevice-AI*" | head -n1)
[ -d "$src_dir" ] || { echo "No source dir found"; exit 1; }

git clone "$REPO" repo
cd repo
git checkout -b "$BRANCH" || git checkout "$BRANCH"

rsync -av --delete --exclude='.git' "$src_dir"/ ./ >/dev/null

git add LICENSE .gitignore SECURITY.md README.md README.es.md
git commit -m "docs: add licenses, policies, and comprehensive README (+ES)" || true

git add pyproject.toml requirements.txt src/
git commit -m "feat(sim): add ultradevice package and CLI" || true

git add data/ examples/ docs/ specs/
git commit -m "docs(specs): add data profiles, scenarios, and specs" || true

git add .github/ .devcontainer/ assets/ Dockerfile Makefile
git commit -m "chore(ci/dev): add CI, dependabot, devcontainer, logo, Dockerfile, Makefile" || true

git push -u origin "$BRANCH"
echo "Pushed branch $BRANCH."
