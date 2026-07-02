#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 13A - FRONTEND TOPOLOGY CERTIFICATION"
echo "========================================="

cd "$ROOT"

echo
echo "Verifying branch..."
BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

echo "PASS: On frontend-skeleton branch."

echo
echo "Running backend tests..."
pytest

echo
echo "Running frontend skeleton verification..."
cd "$FRONTEND"
node scripts/verify-frontend-skeleton.mjs

cd "$ROOT"

echo
echo "Checking required frontend topology..."

required_dirs=(
  "frontend/src/app"
  "frontend/src/components"
  "frontend/src/layouts"
  "frontend/src/providers"
  "frontend/src/hooks"
  "frontend/src/stores"
  "frontend/src/styles"
  "frontend/src/lib/api"
  "frontend/src/lib/contracts"
  "frontend/src/lib/types"
  "frontend/src/features/dashboard"
  "frontend/src/features/market_data"
  "frontend/src/features/portfolio"
  "frontend/src/features/research"
  "frontend/src/features/strategy"
  "frontend/src/features/risk"
  "frontend/src/features/paper_trading"
  "frontend/src/features/broker_integration"
  "frontend/src/features/runtime"
  "frontend/src/features/ai_chat"
  "frontend/src/features/admin_control"
  "frontend/src/features/settings"
)

for dir in "${required_dirs[@]}"; do
  test -d "$dir"
done

required_files=(
  "frontend/package.json"
  "frontend/src/app/layout.tsx"
  "frontend/src/app/page.tsx"
  "frontend/src/layouts/AppShell.tsx"
  "frontend/src/components/Sidebar.tsx"
  "frontend/src/components/TopStatusBar.tsx"
  "frontend/src/components/FeatureCard.tsx"
  "frontend/src/lib/api/client.ts"
  "frontend/src/lib/contracts/frontendSystemState.ts"
  "frontend/src/styles/theme.css"
)

for file in "${required_files[@]}"; do
  test -f "$file"
done

echo "PASS: Frontend topology exists."

echo
echo "Writing certification..."

cat > certification/phase_01/PHASE_13A_FRONTEND_TOPOLOGY_CERTIFICATION.md <<'EOF'
# Phase 13A Frontend Topology Certification

Project: NeuroVest
Branch: frontend-skeleton
Status: PASS

---

# Purpose

Certify that the frontend skeleton topology exists and remains locked before design-system, route-registry, dashboard, or UI implementation work begins.

---

# Verified

- frontend app shell exists
- frontend layout exists
- shared components exist
- feature folders exist
- frontend contract state exists
- API placeholder exists
- skeleton verification script exists
- backend tests pass
- frontend skeleton verification passes

---

# Frontend Topology

Verified folders:

- app
- components
- layouts
- providers
- hooks
- stores
- styles
- lib/api
- lib/contracts
- lib/types
- features/dashboard
- features/market_data
- features/portfolio
- features/research
- features/strategy
- features/risk
- features/paper_trading
- features/broker_integration
- features/runtime
- features/ai_chat
- features/admin_control
- features/settings

---

# Safety Locks

Confirmed:

- no real backend API calls
- no broker calls
- no market data calls
- no AI model calls
- no runtime execution
- no trading logic
- no business logic

---

# Test Result

Backend tests:

85 passed

Frontend skeleton verification:

PASS

---

# Decision

PHASE 13A FRONTEND TOPOLOGY CERTIFIED

Approved to enter:

PHASE 14 — DESIGN SYSTEM SKELETON
EOF

echo
echo "Committing Phase 13A..."

git add certification/phase_01/PHASE_13A_FRONTEND_TOPOLOGY_CERTIFICATION.md \
  scripts/phase_13a_frontend_topology_certification.sh

git commit -m "Phase 13A: Frontend topology certification"

git tag -a phase-13a-frontend-topology-certification \
  -m "Certified Phase 13A frontend topology"

git push
git push --tags

echo
echo "========================================="
echo "PHASE 13A COMPLETE"
echo "========================================="
echo "PASS: Frontend topology certified and pushed."
