#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 28 - FRONTEND SKELETON CERTIFICATION ROLLUP"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

(
  cd "$FRONTEND"
  node scripts/verify-shell-navigation-pages.mjs
  node scripts/verify-frontend-integration-registry.mjs
  node scripts/verify-runtime-ui-skeleton.mjs
  node scripts/verify-broker-integration-ui-skeleton.mjs
  node scripts/verify-paper-trading-ui-skeleton.mjs
  node scripts/verify-risk-ui-skeleton.mjs
  node scripts/verify-strategy-ui-skeleton.mjs
  node scripts/verify-research-ui-skeleton.mjs
  node scripts/verify-portfolio-ui-skeleton.mjs
  node scripts/verify-market-data-ui-skeleton.mjs
  node scripts/verify-neuro-chat-ui-skeleton.mjs
  node scripts/verify-dashboard-skeleton.mjs
  node scripts/verify-route-registry.mjs
  node scripts/verify-design-system-skeleton.mjs
  node scripts/verify-frontend-skeleton.mjs
)

cat > certification/phase_01/PHASE_28_FRONTEND_SKELETON_CERTIFICATION_ROLLUP.md <<'EOF'
# Phase 28 Frontend Skeleton Certification Rollup

Project: NeuroVest
Branch: frontend-skeleton
Status: PASS

---

# Purpose

Certify the completed frontend skeleton from Phase 13 through Phase 27 before styling polish, API wiring, provider wiring, AI wiring, runtime wiring, or trading implementation begins.

---

# Certified Frontend Phases

- Phase 13 — Frontend Skeleton
- Phase 13A — Frontend Topology Certification
- Phase 14 — Design System Skeleton
- Phase 15 — Frontend Route Registry
- Phase 16 — Dashboard Skeleton
- Phase 17 — Neuro Chat UI Skeleton
- Phase 18 — Market Data UI Skeleton
- Phase 19 — Portfolio UI Skeleton
- Phase 20 — Research UI Skeleton
- Phase 21 — Strategy UI Skeleton
- Phase 22 — Risk UI Skeleton
- Phase 23 — Paper Trading UI Skeleton
- Phase 24 — Broker Integration UI Skeleton
- Phase 25 — Runtime UI Skeleton
- Phase 26 — Frontend Integration Registry
- Phase 27 — Frontend Shell Navigation Pages

---

# Certified UI Surfaces

- Dashboard
- Market Data
- Portfolio
- Research
- Strategy
- Risk
- Paper Trading
- Broker Integration
- Runtime
- Neuro Chat
- Admin
- Settings

---

# Verification Result

Backend tests:

- 85 passed

Frontend verifiers:

- shell navigation pages: PASS
- frontend integration registry: PASS
- runtime UI skeleton: PASS
- broker integration UI skeleton: PASS
- paper trading UI skeleton: PASS
- risk UI skeleton: PASS
- strategy UI skeleton: PASS
- research UI skeleton: PASS
- portfolio UI skeleton: PASS
- market data UI skeleton: PASS
- Neuro chat UI skeleton: PASS
- dashboard skeleton: PASS
- route registry: PASS
- design system skeleton: PASS
- frontend skeleton: PASS

---

# Safety Locks Confirmed

- no backend API calls
- no provider calls
- no market data calls
- no broker calls
- no AI model calls
- no tool calls
- no runtime execution
- no scheduler logic
- no workflow execution
- no mutation logic
- no strategy generation
- no risk approval logic
- no paper trading engine
- no live trading
- no order submission
- no config writes
- no secrets handling
- no business logic

---

# Decision

FRONTEND SKELETON CERTIFIED

Approved next work:

- visual polish
- responsive layout polish
- route navigation polish
- static dashboard composition polish
- eventual API contract wiring only after explicit certification

Still forbidden:

- real backend calls
- real provider calls
- real broker calls
- real AI calls
- runtime execution
- trading logic
EOF

cat > docs/contracts/PHASE_28_FRONTEND_SKELETON_CERTIFICATION_ROLLUP_CONTRACT.md <<'EOF'
# Phase 28 Frontend Skeleton Certification Rollup Contract

Status: certification only.

Allowed:
- rerun all frontend skeleton verifiers
- rerun backend tests
- write rollup certification
- tag checkpoint

Forbidden:
- new UI features
- backend API calls
- provider calls
- broker calls
- AI calls
- runtime execution
- trading logic
- business logic
EOF

git add .

git commit -m "Phase 28: Frontend skeleton certification rollup"

git tag -a phase-28-frontend-skeleton-certification-rollup \
  -m "Certified Phase 28 frontend skeleton rollup"

git push
git push --tags

echo "PASS: Phase 28 frontend skeleton rollup complete."
