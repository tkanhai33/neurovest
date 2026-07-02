#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 23 - PAPER TRADING UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/paper_trading/components" \
  "$FRONTEND/src/features/paper_trading/contracts"

cat > "$FRONTEND/src/features/paper_trading/contracts/paperTradingUiState.ts" <<'EOF'
export const paperTradingUiState = {
  phase: "phase_23_paper_trading_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  simulatedOrderEngineEnabled: false,
  simulatedFillEngineEnabled: false,
  pnlLogicEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const paperTradingModules = [
  "Paper Account",
  "Simulated Orders",
  "Simulated Fills",
  "Paper Positions",
  "Paper PnL"
] as const;
EOF

cat > "$FRONTEND/src/features/paper_trading/components/PaperTradingOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { paperTradingModules } from "../contracts/paperTradingUiState";

export function PaperTradingOverviewPanel() {
  return (
    <Card>
      <h2>Paper Trading Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {paperTradingModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/PaperAccountPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function PaperAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Account</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Account" value="Placeholder" />
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Starting Cash" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/SimulatedOrderPlaceholderPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function SimulatedOrderPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Order Shell</h2>
      <StatusPill label="Orders Rejected By Skeleton" />
      <p style={{ color: "var(--muted)" }}>
        Simulated order creation is locked until the paper trading engine is explicitly implemented.
      </p>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/SimulatedFillPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function SimulatedFillPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Fill Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Fill engine locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/PaperPositionPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function PaperPositionPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Position Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Position mutation locked
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/PaperPnLPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function PaperPnLPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper PnL Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Realized PnL" value="Locked" />
        <MetricTile label="Unrealized PnL" value="Locked" />
        <MetricTile label="Currency" value="CAD" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/PaperTradingPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { PaperAccountPlaceholderPanel } from "./PaperAccountPlaceholderPanel";
import { PaperPnLPlaceholderPanel } from "./PaperPnLPlaceholderPanel";
import { PaperPositionPlaceholderPanel } from "./PaperPositionPlaceholderPanel";
import { PaperTradingOverviewPanel } from "./PaperTradingOverviewPanel";
import { SimulatedFillPlaceholderPanel } from "./SimulatedFillPlaceholderPanel";
import { SimulatedOrderPlaceholderPanel } from "./SimulatedOrderPlaceholderPanel";

export function PaperTradingPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Paper Trading"
        subtitle="Static paper trading UI skeleton. Simulated orders, fills, positions, PnL, and broker paths are locked."
      />
      <PaperTradingOverviewPanel />
      <PaperAccountPlaceholderPanel />
      <SimulatedOrderPlaceholderPanel />
      <SimulatedFillPlaceholderPanel />
      <PaperPositionPlaceholderPanel />
      <PaperPnLPlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/paper_trading/components/index.ts" <<'EOF'
export { PaperAccountPlaceholderPanel } from "./PaperAccountPlaceholderPanel";
export { PaperPnLPlaceholderPanel } from "./PaperPnLPlaceholderPanel";
export { PaperPositionPlaceholderPanel } from "./PaperPositionPlaceholderPanel";
export { PaperTradingOverviewPanel } from "./PaperTradingOverviewPanel";
export { PaperTradingPanel } from "./PaperTradingPanel";
export { SimulatedFillPlaceholderPanel } from "./SimulatedFillPlaceholderPanel";
export { SimulatedOrderPlaceholderPanel } from "./SimulatedOrderPlaceholderPanel";
EOF

cat > "$FRONTEND/scripts/verify-paper-trading-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/paper_trading/contracts/paperTradingUiState.ts",
  "src/features/paper_trading/components/PaperTradingOverviewPanel.tsx",
  "src/features/paper_trading/components/PaperAccountPlaceholderPanel.tsx",
  "src/features/paper_trading/components/SimulatedOrderPlaceholderPanel.tsx",
  "src/features/paper_trading/components/SimulatedFillPlaceholderPanel.tsx",
  "src/features/paper_trading/components/PaperPositionPlaceholderPanel.tsx",
  "src/features/paper_trading/components/PaperPnLPlaceholderPanel.tsx",
  "src/features/paper_trading/components/PaperTradingPanel.tsx",
  "src/features/paper_trading/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing paper trading UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "simulate_fill",
  "match_order",
  "calculate_pnl",
  "update_position",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "risk_approved",
  "strategy_signal",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Paper trading UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-paper-trading-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-risk-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-strategy-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-research-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-portfolio-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-market-data-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_23_PAPER_TRADING_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 23 Paper Trading UI Skeleton Contract

Status: skeleton only.

Allowed:
- static paper trading overview
- paper account placeholder
- simulated order shell
- simulated fill placeholder
- paper position placeholder
- paper PnL placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- simulated order engine
- simulated fill engine
- position mutation
- PnL calculations
- risk integration
- strategy integration
- broker calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_23_PAPER_TRADING_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 23 Paper Trading UI Skeleton Certification

Status: PASS

Verified:
- paper trading UI state exists
- paper trading overview exists
- paper account placeholder exists
- simulated order shell exists
- simulated fill placeholder exists
- paper position placeholder exists
- paper PnL placeholder exists
- no backend calls
- no fill engine
- no PnL logic
- no trading logic

Result:
- Phase 23 paper trading UI skeleton is certified.
EOF

git add .
git commit -m "Phase 23: Paper trading UI skeleton"

git tag -a phase-23-paper-trading-ui-skeleton \
  -m "Certified Phase 23 paper trading UI skeleton"

git push
git push --tags

echo "PASS: Phase 23 complete."
