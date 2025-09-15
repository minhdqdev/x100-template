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


# Provenance (prefer the .x100 repo itself; fallback to host project)
SRC_PROJECT_ROOT="$(cd "$SRC_X100_DIR/.." 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || true)"
SRC_REMOTE="local snapshot"; SRC_COMMIT="n/a"
if git -C "$SRC_X100_DIR" rev-parse >/dev/null 2>&1; then
  SRC_REMOTE="$(git -C "$SRC_X100_DIR" remote get-url origin 2>/dev/null || echo "$SRC_REMOTE")"
  SRC_COMMIT="$(git -C "$SRC_X100_DIR" rev-parse --short HEAD 2>/dev/null || echo "$SRC_COMMIT")"
elif [[ -n "$SRC_PROJECT_ROOT" ]]; then
  SRC_REMOTE="$(git -C "$SRC_PROJECT_ROOT" remote get-url origin 2>/dev/null || echo "$SRC_REMOTE")"
  SRC_COMMIT="$(git -C "$SRC_PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "$SRC_COMMIT")"
fi

# ================== Determine target repo (origin of .x100 repo) ==================
TARGET_REPO_URL="$(git -C "$SRC_X100_DIR" remote get-url origin 2>/dev/null || true)"
if [[ -z "$TARGET_REPO_URL" ]]; then
  echo "Could not determine origin remote of .x100 project. Aborting." >&2
  exit 1
fi

# ================== Workspace ==================
TMPDIR="$(mktemp -d -t x100-sync-XXXXXXXX)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "→ Cloning $TARGET_REPO_URL ..."
gh repo clone "$TARGET_REPO_URL" "$TMPDIR/target-repo" >/dev/null
cd "$TMPDIR/target-repo"

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

# ================== Sync workspace into repo root ==================
echo "→ Syncing workspace into repository root"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__/" \
    --exclude=".DS_Store" \
    --exclude="tags" \
    --exclude=".cache" \
    "$SRC_X100_DIR"/ ./
else
  # Fallback using tar, with necessary excludes to protect the repo's .git
  (cd "$SRC_X100_DIR" && tar \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude=".DS_Store" \
    --exclude="tags" \
    --exclude=".cache" \
    -cf - .) | tar xpf -
fi

git add -A

if git diff --cached --quiet; then
  echo "✓ No changes to contribute. Bye."
  exit 0
fi

TITLE="Sync from ${SRC_REMOTE}"
BODY=$(
  cat <<EOF
This PR syncs repository contents from:

- source: ${SRC_REMOTE}
- commit: ${SRC_COMMIT}
- created: $(date -u +"%Y-%m-%d %H:%M:%SZ") (UTC)
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
  # Derive owner/repo from the checked-out repo for an accurate compare URL
  if gh repo view --json nameWithOwner -q .nameWithOwner >/dev/null 2>&1; then
    OWNER_REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
    echo "   https://github.com/$OWNER_REPO/compare/$BASE_BRANCH...$BRANCH"
  else
    echo "   Compare $BRANCH against $BASE_BRANCH on the target repository."
  fi
fi
