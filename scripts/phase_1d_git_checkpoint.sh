#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "========================================="
echo "PHASE 1D - GIT ARCHITECTURE CHECKPOINT"
echo "========================================="
echo

#############################################
# Verify required files exist
#############################################

required=(
  "README.md"
  ".gitignore"
  "pyproject.toml"
  "backend/app/main.py"
  "backend/app/shared/config/settings.py"
  "backend/app/shared/db/session.py"
  "docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md"
  "docs/contracts/FINAL_CONTRACT_CHECKLIST.md"
)

for file in "${required[@]}"; do
  if [ ! -f "$file" ]; then
    echo "ERROR: Missing required file:"
    echo "  $file"
    exit 1
  fi
done

echo "PASS: Required files exist."
echo

#############################################
# Run tests
#############################################

echo "Running certification tests..."
pytest

echo
echo "PASS: All tests passed."
echo

#############################################
# Initialize git
#############################################

if [ ! -d ".git" ]; then
  echo "Initializing git repository..."
  git init
else
  echo "Git repository already exists."
fi

#############################################
# Ensure branch name
#############################################

CURRENT_BRANCH="$(git branch --show-current 2>/dev/null || true)"

if [ -z "$CURRENT_BRANCH" ]; then
  git checkout -b main
elif [ "$CURRENT_BRANCH" != "main" ]; then
  git branch -M main
fi

#############################################
# Create architecture baseline file
#############################################

mkdir -p certification/phase_01

cat > certification/phase_01/PHASE_1D_ARCHITECTURE_BASELINE.md <<'EOF'
# Phase 1D Architecture Baseline

Status: PASS

Certified Foundation:

- Repository skeleton
- Contract documents
- Python runtime
- PostgreSQL skeleton
- FastAPI health endpoint
- Root-level pytest
- Safety locks enabled
- No business logic implemented

This commit represents the first recoverable architecture checkpoint.
EOF

#############################################
# First commit
#############################################

git add .

if git diff --cached --quiet; then
  echo "Nothing new to commit."
else
  git commit -m "Phase 1D: Certified architecture foundation checkpoint"
fi

#############################################
# Create tag
#############################################

if git rev-parse "phase-1-foundation" >/dev/null 2>&1; then
  echo "Tag phase-1-foundation already exists."
else
  git tag -a phase-1-foundation \
    -m "Certified Phase 1 architecture foundation"
fi

#############################################
# Summary
#############################################

echo
echo "========================================="
echo "PHASE 1D COMPLETE"
echo "========================================="
echo
echo "Repository: $ROOT"
echo
echo "Branch:"
git branch --show-current

echo
echo "Latest commit:"
git log --oneline -1

echo
echo "Tags:"
git tag

echo
echo "Recovery commands:"
echo
echo "  git checkout phase-1-foundation"
echo "  git checkout main"
echo "  git reset --hard phase-1-foundation"
echo
echo "PASS: First architecture checkpoint created."
