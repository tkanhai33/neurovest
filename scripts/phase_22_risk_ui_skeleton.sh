#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 22 - RISK UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/risk/components" \
  "$FRONTEND/src/features/risk/contracts"

cat > "$FRONTEND/src/features/risk/contracts/riskUiState.ts" <<'EOF'
export const riskUiState = {
  phase: "phase_22_risk_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  riskMathEnabled: false,
  approvalEngineEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const riskModules = [
  "Exposure Limits",
  "Drawdown Limits",
  "Daily Trade Limits",
  "Approval Decisions",
  "Position Sizing"
] as const;
EOF

cat > "$FRONTEND/src/features/risk/components/RiskOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { riskModules } from "../contracts/riskUiState";

export function RiskOverviewPanel() {
  return (
    <Card>
      <h2>Risk Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {riskModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/ExposurePlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function ExposurePlaceholderPanel() {
  return (
    <Card>
      <h2>Exposure Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Portfolio Exposure" value="Locked" />
        <MetricTile label="Sector Exposure" value="Locked" />
        <MetricTile label="Symbol Exposure" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/DrawdownPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function DrawdownPlaceholderPanel() {
  return (
    <Card>
      <h2>Drawdown Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Daily Drawdown" value="Locked" />
        <MetricTile label="Soft Limit" value="Disabled" />
        <MetricTile label="Hard Limit" value="Disabled" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/DailyLimitPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function DailyLimitPlaceholderPanel() {
  return (
    <Card>
      <h2>Daily Trade Limits</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Max Trades" value="10" />
        <MetricTile label="Used Today" value="Locked" />
        <MetricTile label="Remaining" value="Disabled" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/ApprovalDecisionPlaceholderPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function ApprovalDecisionPlaceholderPanel() {
  return (
    <Card>
      <h2>Approval Decision Shell</h2>
      <StatusPill label="All Approvals Locked" />
      <p style={{ color: "var(--muted)" }}>
        Risk approval engine is not implemented during the skeleton phase.
      </p>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/RiskPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { ApprovalDecisionPlaceholderPanel } from "./ApprovalDecisionPlaceholderPanel";
import { DailyLimitPlaceholderPanel } from "./DailyLimitPlaceholderPanel";
import { DrawdownPlaceholderPanel } from "./DrawdownPlaceholderPanel";
import { ExposurePlaceholderPanel } from "./ExposurePlaceholderPanel";
import { RiskOverviewPanel } from "./RiskOverviewPanel";

export function RiskPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Risk"
        subtitle="Static risk UI skeleton. Risk math, approvals, trading, and broker paths are locked."
      />
      <RiskOverviewPanel />
      <ExposurePlaceholderPanel />
      <DrawdownPlaceholderPanel />
      <DailyLimitPlaceholderPanel />
      <ApprovalDecisionPlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/risk/components/index.ts" <<'EOF'
export { ApprovalDecisionPlaceholderPanel } from "./ApprovalDecisionPlaceholderPanel";
export { DailyLimitPlaceholderPanel } from "./DailyLimitPlaceholderPanel";
export { DrawdownPlaceholderPanel } from "./DrawdownPlaceholderPanel";
export { ExposurePlaceholderPanel } from "./ExposurePlaceholderPanel";
export { RiskOverviewPanel } from "./RiskOverviewPanel";
export { RiskPanel } from "./RiskPanel";
EOF

cat > "$FRONTEND/scripts/verify-risk-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/risk/contracts/riskUiState.ts",
  "src/features/risk/components/RiskOverviewPanel.tsx",
  "src/features/risk/components/ExposurePlaceholderPanel.tsx",
  "src/features/risk/components/DrawdownPlaceholderPanel.tsx",
  "src/features/risk/components/DailyLimitPlaceholderPanel.tsx",
  "src/features/risk/components/ApprovalDecisionPlaceholderPanel.tsx",
  "src/features/risk/components/RiskPanel.tsx",
  "src/features/risk/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing risk UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "calculate_position_size",
  "calculate_drawdown",
  "calculate_exposure",
  "approve_trade",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Risk UI skeleton verified.");
EOF

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

cat > docs/contracts/PHASE_22_RISK_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 22 Risk UI Skeleton Contract

Status: skeleton only.

Allowed:
- static risk overview
- exposure placeholder
- drawdown placeholder
- daily trade limit placeholder
- approval decision placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- risk calculations
- position sizing
- approval engine
- paper trading
- broker calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_22_RISK_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 22 Risk UI Skeleton Certification

Status: PASS

Verified:
- risk UI state exists
- risk overview panel exists
- exposure placeholder panel exists
- drawdown placeholder panel exists
- daily limit placeholder panel exists
- approval decision placeholder exists
- no backend calls
- no risk math
- no approval logic
- no trading logic

Result:
- Phase 22 risk UI skeleton is certified.
EOF

git add .
git commit -m "Phase 22: Risk UI skeleton"

git tag -a phase-22-risk-ui-skeleton \
  -m "Certified Phase 22 risk UI skeleton"

git push
git push --tags

echo "PASS: Phase 22 complete."
