#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 19 - PORTFOLIO UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/portfolio/components" \
  "$FRONTEND/src/features/portfolio/contracts"

cat > "$FRONTEND/src/features/portfolio/contracts/portfolioUiState.ts" <<'EOF'
export const portfolioUiState = {
  phase: "phase_19_portfolio_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  portfolioMutationEnabled: false,
  tradingEnabled: false
} as const;

export const portfolioHoldings = [
  "RY.TO",
  "VFV.TO",
  "VUN.TO"
] as const;
EOF

cat > "$FRONTEND/src/features/portfolio/components/PortfolioSummaryPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function PortfolioSummaryPanel() {
  return (
    <Card>
      <h2>Portfolio Summary</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Total Value" value="Locked" />
        <MetricTile label="Cash" value="Locked" />
        <MetricTile label="Holdings" value="Placeholder" />
        <MetricTile label="PnL" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/portfolio/components/HoldingsPlaceholderPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { portfolioHoldings } from "../contracts/portfolioUiState";

export function HoldingsPlaceholderPanel() {
  return (
    <Card>
      <h2>Holdings Placeholder</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {portfolioHoldings.map((symbol) => (
          <Badge key={symbol} label={`${symbol}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/portfolio/components/CashBalancePanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function CashBalancePanel() {
  return (
    <Card>
      <h2>Cash & Balance</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Available Cash" value="Locked" />
        <MetricTile label="Buying Power" value="Disabled" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/portfolio/components/AllocationPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function AllocationPlaceholderPanel() {
  return (
    <Card>
      <h2>Allocation Placeholder</h2>
      <div style={{ height: "180px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Allocation chart locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/portfolio/components/PortfolioPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { AllocationPlaceholderPanel } from "./AllocationPlaceholderPanel";
import { CashBalancePanel } from "./CashBalancePanel";
import { HoldingsPlaceholderPanel } from "./HoldingsPlaceholderPanel";
import { PortfolioSummaryPanel } from "./PortfolioSummaryPanel";

export function PortfolioPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Portfolio"
        subtitle="Static portfolio UI skeleton. Broker, backend, and mutation paths are locked."
      />
      <PortfolioSummaryPanel />
      <CashBalancePanel />
      <HoldingsPlaceholderPanel />
      <AllocationPlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/portfolio/components/index.ts" <<'EOF'
export { AllocationPlaceholderPanel } from "./AllocationPlaceholderPanel";
export { CashBalancePanel } from "./CashBalancePanel";
export { HoldingsPlaceholderPanel } from "./HoldingsPlaceholderPanel";
export { PortfolioPanel } from "./PortfolioPanel";
export { PortfolioSummaryPanel } from "./PortfolioSummaryPanel";
EOF

cat > "$FRONTEND/scripts/verify-portfolio-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/portfolio/contracts/portfolioUiState.ts",
  "src/features/portfolio/components/PortfolioSummaryPanel.tsx",
  "src/features/portfolio/components/HoldingsPlaceholderPanel.tsx",
  "src/features/portfolio/components/CashBalancePanel.tsx",
  "src/features/portfolio/components/AllocationPlaceholderPanel.tsx",
  "src/features/portfolio/components/PortfolioPanel.tsx",
  "src/features/portfolio/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing portfolio UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "sync_broker",
  "update_position",
  "calculate_pnl",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Portfolio UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-portfolio-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-market-data-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_19_PORTFOLIO_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 19 Portfolio UI Skeleton Contract

Status: skeleton only.

Allowed:
- static portfolio summary
- holdings placeholder
- cash/balance placeholder
- allocation placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- broker calls
- portfolio mutation
- transaction logic
- PnL calculations
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_19_PORTFOLIO_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 19 Portfolio UI Skeleton Certification

Status: PASS

Verified:
- portfolio UI state exists
- portfolio summary panel exists
- holdings placeholder panel exists
- cash/balance panel exists
- allocation placeholder panel exists
- no backend calls
- no broker calls
- no portfolio mutation
- no trading logic

Result:
- Phase 19 portfolio UI skeleton is certified.
EOF

git add .
git commit -m "Phase 19: Portfolio UI skeleton"

git tag -a phase-19-portfolio-ui-skeleton \
  -m "Certified Phase 19 portfolio UI skeleton"

git push
git push --tags

echo "PASS: Phase 19 complete."
