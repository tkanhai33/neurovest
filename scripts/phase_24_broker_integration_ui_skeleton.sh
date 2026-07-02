#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 24 - BROKER INTEGRATION UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/broker_integration/components" \
  "$FRONTEND/src/features/broker_integration/contracts"

cat > "$FRONTEND/src/features/broker_integration/contracts/brokerIntegrationUiState.ts" <<'EOF'
export const brokerIntegrationUiState = {
  phase: "phase_24_broker_integration_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  authFlowEnabled: false,
  tokenStorageEnabled: false,
  accountSyncEnabled: false,
  orderSubmissionEnabled: false,
  liveTradingEnabled: false
} as const;

export const brokerIntegrationModules = [
  "Provider Boundary",
  "Connection Status",
  "Auth Locked",
  "Read-Only Account",
  "Order Submission Locked"
] as const;
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { brokerIntegrationModules } from "../contracts/brokerIntegrationUiState";

export function BrokerOverviewPanel() {
  return (
    <Card>
      <h2>Broker Integration Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {brokerIntegrationModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerProviderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function BrokerProviderPanel() {
  return (
    <Card>
      <h2>Provider Boundary</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Provider" value="SnapTrade" />
        <MetricTile label="Mode" value="Skeleton" />
        <MetricTile label="Calls" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerConnectionStatusPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function BrokerConnectionStatusPanel() {
  return (
    <Card>
      <h2>Connection Status</h2>
      <StatusPill label="Not Connected" />
      <StatusPill label="Read-Only Locked" />
      <StatusPill label="Live Trading Locked" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerAuthLockedPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function BrokerAuthLockedPanel() {
  return (
    <Card>
      <h2>Authentication Locked</h2>
      <StatusPill label="Auth Flow Disabled" />
      <StatusPill label="Token Storage Disabled" />
      <p style={{ color: "var(--muted)" }}>
        Broker authentication and token storage are not implemented during the skeleton phase.
      </p>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerAccountPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function BrokerAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Read-Only Account Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Account Sync" value="Locked" />
        <MetricTile label="Positions" value="Disabled" />
        <MetricTile label="Balances" value="Disabled" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerOrderLockedPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function BrokerOrderLockedPanel() {
  return (
    <Card>
      <h2>Order Submission Locked</h2>
      <StatusPill label="Orders Disabled" />
      <StatusPill label="Execution Disabled" />
      <StatusPill label="Live Trading Disabled" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/BrokerIntegrationPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { BrokerAccountPlaceholderPanel } from "./BrokerAccountPlaceholderPanel";
import { BrokerAuthLockedPanel } from "./BrokerAuthLockedPanel";
import { BrokerConnectionStatusPanel } from "./BrokerConnectionStatusPanel";
import { BrokerOrderLockedPanel } from "./BrokerOrderLockedPanel";
import { BrokerOverviewPanel } from "./BrokerOverviewPanel";
import { BrokerProviderPanel } from "./BrokerProviderPanel";

export function BrokerIntegrationPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Broker Integration"
        subtitle="Static broker UI skeleton. Auth, tokens, account sync, order submission, and live trading are locked."
      />
      <BrokerOverviewPanel />
      <BrokerProviderPanel />
      <BrokerConnectionStatusPanel />
      <BrokerAuthLockedPanel />
      <BrokerAccountPlaceholderPanel />
      <BrokerOrderLockedPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/broker_integration/components/index.ts" <<'EOF'
export { BrokerAccountPlaceholderPanel } from "./BrokerAccountPlaceholderPanel";
export { BrokerAuthLockedPanel } from "./BrokerAuthLockedPanel";
export { BrokerConnectionStatusPanel } from "./BrokerConnectionStatusPanel";
export { BrokerIntegrationPanel } from "./BrokerIntegrationPanel";
export { BrokerOrderLockedPanel } from "./BrokerOrderLockedPanel";
export { BrokerOverviewPanel } from "./BrokerOverviewPanel";
export { BrokerProviderPanel } from "./BrokerProviderPanel";
EOF

cat > "$FRONTEND/scripts/verify-broker-integration-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/broker_integration/contracts/brokerIntegrationUiState.ts",
  "src/features/broker_integration/components/BrokerOverviewPanel.tsx",
  "src/features/broker_integration/components/BrokerProviderPanel.tsx",
  "src/features/broker_integration/components/BrokerConnectionStatusPanel.tsx",
  "src/features/broker_integration/components/BrokerAuthLockedPanel.tsx",
  "src/features/broker_integration/components/BrokerAccountPlaceholderPanel.tsx",
  "src/features/broker_integration/components/BrokerOrderLockedPanel.tsx",
  "src/features/broker_integration/components/BrokerIntegrationPanel.tsx",
  "src/features/broker_integration/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing broker integration UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "import snaptrade",
  "SnapTradeClient",
  "access_token",
  "refresh_token",
  "submit_order",
  "place_order",
  "execute_trade",
  "live_trade",
  "broker_client",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Broker integration UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-broker-integration-ui-skeleton.mjs)
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

cat > docs/contracts/PHASE_24_BROKER_INTEGRATION_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 24 Broker Integration UI Skeleton Contract

Status: skeleton only.

Allowed:
- static broker integration overview
- provider boundary placeholder
- connection status placeholder
- authentication locked panel
- read-only account placeholder
- order submission locked panel
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- real broker calls
- broker authentication
- token storage
- account sync
- order submission
- live trading
- execution logic
- business logic
EOF

cat > certification/phase_01/PHASE_24_BROKER_INTEGRATION_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 24 Broker Integration UI Skeleton Certification

Status: PASS

Verified:
- broker integration UI state exists
- broker overview panel exists
- provider boundary panel exists
- connection status panel exists
- auth locked panel exists
- account placeholder panel exists
- order locked panel exists
- no backend calls
- no broker calls
- no token storage
- no order submission
- no live trading

Result:
- Phase 24 broker integration UI skeleton is certified.
EOF

git add .
git commit -m "Phase 24: Broker integration UI skeleton"

git tag -a phase-24-broker-integration-ui-skeleton \
  -m "Certified Phase 24 broker integration UI skeleton"

git push
git push --tags

echo "PASS: Phase 24 complete."
