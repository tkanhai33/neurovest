#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 26 - FRONTEND INTEGRATION REGISTRY"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/lib/integration"

cat > "$FRONTEND/src/lib/integration/featureIntegrationRegistry.ts" <<'EOF'
import { BrokerIntegrationPanel } from "../../features/broker_integration/components";
import { DashboardShell } from "../../features/dashboard/components";
import { MarketDataPanel } from "../../features/market_data/components";
import { NeuroChatPanel } from "../../features/ai_chat/components";
import { PaperTradingPanel } from "../../features/paper_trading/components";
import { PortfolioPanel } from "../../features/portfolio/components";
import { ResearchPanel } from "../../features/research/components";
import { RiskPanel } from "../../features/risk/components";
import { RuntimePanel } from "../../features/runtime/components";
import { StrategyPanel } from "../../features/strategy/components";

export type IntegratedFeatureKey =
  | "dashboard"
  | "market_data"
  | "portfolio"
  | "research"
  | "strategy"
  | "risk"
  | "paper_trading"
  | "broker_integration"
  | "runtime"
  | "ai_chat";

export const featureIntegrationState = {
  phase: "phase_26_frontend_integration_registry",
  integrationOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false,
  runtimeExecutionEnabled: false,
  tradingEnabled: false
} as const;

export const integratedFeatures = [
  { key: "dashboard", label: "Dashboard", component: DashboardShell, locked: true },
  { key: "market_data", label: "Market Data", component: MarketDataPanel, locked: true },
  { key: "portfolio", label: "Portfolio", component: PortfolioPanel, locked: true },
  { key: "research", label: "Research", component: ResearchPanel, locked: true },
  { key: "strategy", label: "Strategy", component: StrategyPanel, locked: true },
  { key: "risk", label: "Risk", component: RiskPanel, locked: true },
  { key: "paper_trading", label: "Paper Trading", component: PaperTradingPanel, locked: true },
  { key: "broker_integration", label: "Broker Integration", component: BrokerIntegrationPanel, locked: true },
  { key: "runtime", label: "Runtime", component: RuntimePanel, locked: true },
  { key: "ai_chat", label: "Neuro Chat", component: NeuroChatPanel, locked: true }
] as const;
EOF

cat > "$FRONTEND/src/components/Sidebar.tsx" <<'EOF'
import { frontendRoutes } from "../lib/routes/routeRegistry";

export function Sidebar() {
  return (
    <aside style={{ background: "var(--panel)", padding: "24px", borderRight: "1px solid var(--panel-soft)" }}>
      <h1 style={{ marginTop: 0 }}>NeuroVest</h1>
      <p style={{ color: "var(--muted)" }}>Skeleton UI</p>
      <nav style={{ display: "grid", gap: "10px" }}>
        {frontendRoutes.map((route) => (
          <div key={route.key} style={{ color: "var(--text)" }}>
            {route.label} {route.locked ? "🔒" : ""}
          </div>
        ))}
      </nav>
    </aside>
  );
}
EOF

cat > "$FRONTEND/scripts/verify-frontend-integration-registry.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/lib/integration/featureIntegrationRegistry.ts",
  "src/components/Sidebar.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing frontend integration file: ${file}`);
}

const registryText = readFileSync("src/lib/integration/featureIntegrationRegistry.ts", "utf8");

const expected = [
  "DashboardShell",
  "MarketDataPanel",
  "PortfolioPanel",
  "ResearchPanel",
  "StrategyPanel",
  "RiskPanel",
  "PaperTradingPanel",
  "BrokerIntegrationPanel",
  "RuntimePanel",
  "NeuroChatPanel"
];

for (const item of expected) {
  if (!registryText.includes(item)) {
    throw new Error(`Missing integrated feature: ${item}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "ollama.chat",
  "ollama.generate",
  "setInterval",
  "setTimeout",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Frontend integration registry verified.");
EOF

(
  cd "$FRONTEND"
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

cat > docs/contracts/PHASE_26_FRONTEND_INTEGRATION_REGISTRY_CONTRACT.md <<'EOF'
# Phase 26 Frontend Integration Registry Contract

Status: skeleton only.

Allowed:
- feature integration registry
- registered feature panel metadata
- locked feature state
- sidebar registry consumption
- verification script
- certification artifact

Forbidden:
- backend API calls
- provider calls
- broker calls
- AI model calls
- runtime execution
- scheduler logic
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_26_FRONTEND_INTEGRATION_REGISTRY_CERTIFICATION.md <<'EOF'
# Phase 26 Frontend Integration Registry Certification

Status: PASS

Verified:
- frontend integration registry exists
- dashboard panel registered
- market data panel registered
- portfolio panel registered
- research panel registered
- strategy panel registered
- risk panel registered
- paper trading panel registered
- broker integration panel registered
- runtime panel registered
- Neuro chat panel registered
- sidebar consumes route registry
- no backend calls
- no provider calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic

Result:
- Phase 26 frontend integration registry is certified.
EOF

git add .
git commit -m "Phase 26: Frontend integration registry"

git tag -a phase-26-frontend-integration-registry \
  -m "Certified Phase 26 frontend integration registry"

git push
git push --tags

echo "PASS: Phase 26 complete."
