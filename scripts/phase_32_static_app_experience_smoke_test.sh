#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 32 - STATIC APP EXPERIENCE SMOKE TEST"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

if [ -x "$ROOT/backend/.venv/bin/pytest" ]; then
  "$ROOT/backend/.venv/bin/pytest"
else
  pytest
fi

(
  cd "$FRONTEND"
  node scripts/verify-navigation-responsive-layout-polish.mjs
  node scripts/verify-dashboard-visual-composition.mjs
  node scripts/verify-visual-polish-foundation.mjs
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

cat > "$FRONTEND/scripts/verify-static-app-experience-smoke.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const routes = [
  "src/app/page.tsx",
  "src/app/market-data/page.tsx",
  "src/app/portfolio/page.tsx",
  "src/app/research/page.tsx",
  "src/app/strategy/page.tsx",
  "src/app/risk/page.tsx",
  "src/app/paper-trading/page.tsx",
  "src/app/broker-integration/page.tsx",
  "src/app/runtime/page.tsx",
  "src/app/ai-chat/page.tsx",
  "src/app/admin/page.tsx",
  "src/app/settings/page.tsx"
];

for (const route of routes) {
  if (!existsSync(route)) throw new Error(`Missing static app route: ${route}`);
}

const requiredShell = [
  "src/layouts/AppShell.tsx",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/styles/theme.css",
  "src/lib/routes/routeRegistry.ts",
  "src/lib/integration/featureIntegrationRegistry.ts"
];

for (const file of requiredShell) {
  if (!existsSync(file)) throw new Error(`Missing shell file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "useEffect(",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "ollama.chat",
  "ollama.generate",
  "setInterval",
  "setTimeout",
  "access_token",
  "refresh_token"
];

for (const file of [...routes, ...requiredShell]) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Static app experience smoke verified.");
EOF

(
  cd "$FRONTEND"
  node scripts/verify-static-app-experience-smoke.mjs
)

cat > docs/contracts/PHASE_32_STATIC_APP_EXPERIENCE_SMOKE_TEST_CONTRACT.md <<'EOF'
# Phase 32 Static App Experience Smoke Test Contract

Status: verification only.

Allowed:
- rerun backend tests
- rerun all frontend verifiers
- verify static route pages
- verify shell files
- write smoke certification
- tag checkpoint

Forbidden:
- new UI features
- backend API calls
- provider calls
- broker calls
- AI calls
- runtime execution
- scheduler logic
- trading logic
- secrets handling
- business logic
EOF

cat > certification/phase_01/PHASE_32_STATIC_APP_EXPERIENCE_SMOKE_TEST_CERTIFICATION.md <<'EOF'
# Phase 32 Static App Experience Smoke Test Certification

Status: PASS

Verified:
- backend tests pass
- all frontend verifiers pass
- dashboard route exists
- market data route exists
- portfolio route exists
- research route exists
- strategy route exists
- risk route exists
- paper trading route exists
- broker integration route exists
- runtime route exists
- Neuro chat route exists
- admin route exists
- settings route exists
- app shell exists
- sidebar exists
- top status bar exists
- route registry exists
- feature integration registry exists
- no backend calls
- no provider calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic
- no secrets handling

Result:
- Phase 32 static app experience smoke test is certified.
EOF

git add .
git commit -m "Phase 32: Static app experience smoke test"

git tag -a phase-32-static-app-experience-smoke-test \
  -m "Certified Phase 32 static app experience smoke test"

git push
git push --tags

echo "PASS: Phase 32 complete."
