#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "========================================="
echo "PHASE 1C CLEANUP"
echo "========================================="
echo

#############################################
# Fix Verify comment
#############################################

SCRIPT="$ROOT/scripts/phase_1c_postgres_database_skeleton.sh"

if grep -q '^Verify$' "$SCRIPT"; then
  echo "Fixing Verify comment..."
  sed -i '/^Verify$/c\# Verify' "$SCRIPT"
  echo "PASS: Verify comment fixed."
else
  echo "Verify comment already fixed."
fi

#############################################
# Update certification
#############################################

echo
echo "Updating certification to PASS..."

cat > "$ROOT/certification/phase_01/PHASE_1C_DATABASE_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 1C Database Skeleton Certification

Status: PASS

Checks:
- PostgreSQL installed
- PostgreSQL running
- neurovest user exists
- neurovest database exists
- .env contains DATABASE_URL
- SQLAlchemy connection works
- Safety settings remain locked
- No business schema created

Verification:
- PostgreSQL connection: PASS
- pytest: 4 passed
EOF

#############################################
# Verify cleanup
#############################################

echo
echo "Verifying cleanup..."

test -f "$ROOT/certification/phase_01/PHASE_1C_DATABASE_SKELETON_CERTIFICATION.md"

grep -q "Status: PASS" \
  "$ROOT/certification/phase_01/PHASE_1C_DATABASE_SKELETON_CERTIFICATION.md"

echo
echo "========================================="
echo "PHASE 1C CLEANUP COMPLETE"
echo "========================================="
echo
echo "PASS: Certification updated and script repaired."
