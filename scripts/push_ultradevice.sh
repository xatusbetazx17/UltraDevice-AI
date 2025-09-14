#!/usr/bin/env bash
set -euo pipefail
ZIP_FILE="${1:-UltraDevice-AI_pro.zip}"
REPO_URL="${2:-https://github.com/xatusbetazx17/UltraDevice-AI.git}"

if [ ! -f "$ZIP_FILE" ]; then
  echo "ERROR: ZIP file '$ZIP_FILE' not found."
  exit 1
fi

if git ls-remote --heads "$REPO_URL" main >/dev/null 2>&1 && git ls-remote --heads "$REPO_URL" main | grep -q .; then
  BRANCH="main"
elif git ls-remote --heads "$REPO_URL" master >/dev/null 2>&1 && git ls-remote --heads "$REPO_URL" master | grep -q .; then
  BRANCH="master"
else
  BRANCH="main"
fi

WORKDIR="$(mktemp -d)"
echo "Working directory: $WORKDIR"
unzip -q "$ZIP_FILE" -d "$WORKDIR"

SRC_DIR="$(find "$WORKDIR" -maxdepth 2 -type d -name 'UltraDevice-AI*' | head -n1)"
[ -d "$SRC_DIR" ] || { echo "Source dir not found"; exit 1; }

CLONE_DIR="$WORKDIR/repo"
git clone "$REPO_URL" "$CLONE_DIR" >/dev/null

rsync -av --delete --exclude='.git' "$SRC_DIR"/ "$CLONE_DIR"/ >/dev/null

cd "$CLONE_DIR"
git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH"
git add -A
git commit -m "feat: import simulator, docs, CI, and assets (v0.2.0)" || true
git push origin "$BRANCH"
echo "Done."
