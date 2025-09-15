#!/usr/bin/env bash
set -euo pipefail

# ================== Config ==================
TEMPLATE_REPO="${X100_TEMPLATE_REPO:-minhdqdev/x100-template}"  # owner/repo
[[ "$TEMPLATE_REPO" == "owner/x100-template" ]] && {
  echo "Please set X100_TEMPLATE_REPO=owner/x100-template"; exit 1; }

# ================== Checks ==================
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1"; exit 1; }; }
need git; need gh
gh auth status -h github.com >/dev/null || { echo "Run: gh auth login"; exit 1; }

# Path to the .x100 we're syncing FROM (this script lives inside it)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_X100_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"   # points to .x100


# Optional provenance from the host project (if it's a git repo)
SRC_PROJECT_ROOT="$(cd "$SRC_X100_DIR/.." 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || true)"
SRC_REMOTE="local snapshot"; SRC_COMMIT="n/a"
if [[ -n "$SRC_PROJECT_ROOT" ]]; then
  SRC_REMOTE="$(git -C "$SRC_PROJECT_ROOT" remote get-url origin 2>/dev/null || echo "$SRC_REMOTE")"
  SRC_COMMIT="$(git -C "$SRC_PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "$SRC_COMMIT")"
fi

# ================== Workspace ==================
TMPDIR="$(mktemp -d -t x100-sync-XXXXXXXX)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "→ Cloning $TEMPLATE_REPO ..."
gh repo clone "$TEMPLATE_REPO" "$TMPDIR/x100-template" >/dev/null
cd "$TMPDIR/x100-template"

# Choose base branch (prefer 'develop')
TARGET_BRANCH="${X100_BASE_BRANCH:-develop}"
if git ls-remote --exit-code --heads origin "$TARGET_BRANCH" >/dev/null 2>&1; then
  BASE_BRANCH="$TARGET_BRANCH"
else
  # Fall back to repo default branch, then to TARGET_BRANCH
  git remote set-head origin -a >/dev/null 2>&1 || true
  BASE_BRANCH="$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | cut -d/ -f2 || true)"
  BASE_BRANCH="${BASE_BRANCH:-$TARGET_BRANCH}"
fi

# Generate a portable 6-char suffix (sha256sum or shasum)
_hash_input="$(date +%s%N)$RANDOM"
if command -v sha256sum >/dev/null 2>&1; then
  RAND_SUFFIX="$(printf '%s' "$_hash_input" | sha256sum | cut -c1-6)"
else
  RAND_SUFFIX="$(printf '%s' "$_hash_input" | shasum -a 256 | cut -c1-6)"
fi
BRANCH="x100-sync/$(date +%Y%m%d-%H%M%S)-$RAND_SUFFIX"
git checkout -b "$BRANCH" "origin/$BASE_BRANCH"

# ================== Sync whole repository ==================
# Determine source project root (host repo)
if [[ -z "$SRC_PROJECT_ROOT" ]]; then
  SRC_PROJECT_ROOT="$(cd "$SRC_X100_DIR/.." 2>/dev/null && pwd)"
fi
if [[ -z "$SRC_PROJECT_ROOT" ]]; then
  echo "Could not determine source project root. Aborting." >&2
  exit 1
fi

echo "→ Syncing entire repository from: $SRC_PROJECT_ROOT"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__/" \
    --exclude=".DS_Store" \
    --exclude="node_modules" \
    --exclude=".pnpm-store" \
    --exclude="tags" \
    --exclude=".cache" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude=".mypy_cache" \
    "$SRC_PROJECT_ROOT"/ ./
else
  (cd "$SRC_PROJECT_ROOT" && tar --exclude .git -cf - .) | tar xpf -
  find . -name ".git" -type d -prune -o -name "__pycache__" -type d -exec rm -rf {} + || true
fi

git add -A

if git diff --cached --quiet; then
  echo "✓ No changes to contribute. Bye."
  exit 0
fi

TITLE="Sync repository from ${SRC_REMOTE}"
BODY=$(
  cat <<EOF
This PR updates the repository by syncing from:

- source: ${SRC_REMOTE}
- commit: ${SRC_COMMIT}
- created: $(date -u +"%Y-%m-%d %H:%M:%SZ") (UTC)

All changes reflect the current state of the source repository (excluding VCS/caches).
EOF
)

git commit -m "$TITLE" -m "$BODY"
git push -u origin "$BRANCH" >/dev/null

# ================== Open PR ==================
PR_DRAFT_FLAG=""
if [[ "${X100_DRAFT:-0}" == "1" ]]; then PR_DRAFT_FLAG="--draft"; fi

echo "→ Creating PR to $BASE_BRANCH ..."
if gh pr create -B "$BASE_BRANCH" -t "$TITLE" -b "$BODY" ${PR_DRAFT_FLAG:+$PR_DRAFT_FLAG} >/dev/null; then
  gh pr view --json url -q .url || true
  echo "✓ PR created."
else
  echo "⚠️ Could not auto-create PR. Open manually:"
  echo "   https://github.com/$TEMPLATE_REPO/compare/$BASE_BRANCH...$BRANCH"
fi
