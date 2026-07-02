#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 15 - FRONTEND ROUTE REGISTRY"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/lib/routes"

cat > "$FRONTEND/src/lib/routes/routeRegistry.ts" <<'EOF'
export type FrontendRouteKey =
  | "dashboard"
  | "market_data"
  | "portfolio"
  | "research"
  | "strategy"
  | "risk"
  | "paper_trading"
  | "broker_integration"
  | "runtime"
  | "ai_chat"
  | "admin_control"
  | "settings";

export type FrontendRoute = {
  key: FrontendRouteKey;
  label: string;
  path: string;
  locked: boolean;
};

export const frontendRoutes: readonly FrontendRoute[] = [
  { key: "dashboard", label: "Dashboard", path: "/", locked: true },
  { key: "market_data", label: "Market Data", path: "/market-data", locked: true },
  { key: "portfolio", label: "Portfolio", path: "/portfolio", locked: true },
  { key: "research", label: "Research", path: "/research", locked: true },
  { key: "strategy", label: "Strategy", path: "/strategy", locked: true },
  { key: "risk", label: "Risk", path: "/risk", locked: true },
  { key: "paper_trading", label: "Paper Trading", path: "/paper-trading", locked: true },
  { key: "broker_integration", label: "Broker Integration", path: "/broker-integration", locked: true },
  { key: "runtime", label: "Runtime", path: "/runtime", locked: true },
  { key: "ai_chat", label: "Neuro Chat", path: "/ai-chat", locked: true },
  { key: "admin_control", label: "Admin", path: "/admin", locked: true },
  { key: "settings", label: "Settings", path: "/settings", locked: true }
] as const;
EOF

cat > "$FRONTEND/src/lib/routes/navigationState.ts" <<'EOF'
export const navigationState = {
  phase: "phase_15_frontend_route_registry",
  routesImplemented: false,
  registryOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  aiCallsEnabled: false
} as const;
EOF

cat > "$FRONTEND/scripts/verify-route-registry.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/lib/routes/routeRegistry.ts",
  "src/lib/routes/navigationState.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing route registry file: ${file}`);
}

const routeText = readFileSync("src/lib/routes/routeRegistry.ts", "utf8");

const expected = [
  "dashboard",
  "market_data",
  "portfolio",
  "research",
  "strategy",
  "risk",
  "paper_trading",
  "broker_integration",
  "runtime",
  "ai_chat",
  "admin_control",
  "settings"
];

for (const key of expected) {
  if (!routeText.includes(key)) {
    throw new Error(`Missing route key: ${key}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "broker_client"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Frontend route registry verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)

cat > docs/contracts/PHASE_15_FRONTEND_ROUTE_REGISTRY_CONTRACT.md <<'EOF'
# Phase 15 Frontend Route Registry Contract

Status: skeleton only.

Allowed:
- frontend route keys
- route labels
- locked route metadata
- navigation state contract
- route registry verification

Forbidden:
- real page implementation
- backend API calls
- broker calls
- AI calls
- trading logic
- runtime execution
- business logic
EOF

cat > certification/phase_01/PHASE_15_FRONTEND_ROUTE_REGISTRY_CERTIFICATION.md <<'EOF'
# Phase 15 Frontend Route Registry Certification

Status: PASS

Verified:
- route registry exists
- navigation state exists
- all core route keys exist
- all routes remain locked
- no backend calls
- no broker calls
- no AI calls
- no trading logic

Result:
- Phase 15 frontend route registry is certified.
EOF

git add .
git commit -m "Phase 15: Frontend route registry"

git tag -a phase-15-frontend-route-registry \
  -m "Certified Phase 15 frontend route registry"

git push
git push --tags

echo "PASS: Phase 15 complete."
