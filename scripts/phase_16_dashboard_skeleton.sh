#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 16 - DASHBOARD SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/dashboard/components" \
  "$FRONTEND/src/features/dashboard/contracts"

cat > "$FRONTEND/src/features/dashboard/contracts/dashboardState.ts" <<'EOF'
export const dashboardState = {
  phase: "phase_16_dashboard_skeleton",
  dashboardImplemented: false,
  staticOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  aiCallsEnabled: false,
  runtimeEnabled: false
} as const;

export const dashboardStacks = [
  "Identity/Auth",
  "Safety/Governance",
  "Market Data",
  "Portfolio",
  "Research",
  "Strategy",
  "Risk",
  "Paper Trading",
  "Broker Integration",
  "Runtime",
  "AI Chat",
  "Global Registry"
] as const;
EOF

cat > "$FRONTEND/src/features/dashboard/components/SystemLockPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function SystemLockPanel() {
  return (
    <Card>
      <h2>System Locks</h2>
      <StatusPill label="Live Trading Locked" />
      <StatusPill label="Broker Orders Locked" />
      <StatusPill label="Runtime Locked" />
      <StatusPill label="AI Tool Use Locked" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/StackOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { dashboardStacks } from "../contracts/dashboardState";

export function StackOverviewPanel() {
  return (
    <Card>
      <h2>Stack Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {dashboardStacks.map((stack) => (
          <Badge key={stack} label={`${stack}: Skeleton`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/PhaseProgressPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function PhaseProgressPanel() {
  return (
    <Card>
      <h2>Phase Progress</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Backend" value="Certified" />
        <MetricTile label="Frontend" value="Skeleton" />
        <MetricTile label="Tests" value="85 Passing" />
        <MetricTile label="Trading" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/DashboardShell.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";

export function DashboardShell() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="NeuroVest Dashboard"
        subtitle="Static dashboard skeleton. All execution paths remain locked."
      />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/index.ts" <<'EOF'
export { DashboardShell } from "./DashboardShell";
export { PhaseProgressPanel } from "./PhaseProgressPanel";
export { StackOverviewPanel } from "./StackOverviewPanel";
export { SystemLockPanel } from "./SystemLockPanel";
EOF

cat > "$FRONTEND/src/app/page.tsx" <<'EOF'
import { DashboardShell } from "../features/dashboard/components";
import { AppShell } from "../layouts/AppShell";

export default function HomePage() {
  return (
    <AppShell>
      <DashboardShell />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/scripts/verify-dashboard-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/contracts/dashboardState.ts",
  "src/features/dashboard/components/SystemLockPanel.tsx",
  "src/features/dashboard/components/StackOverviewPanel.tsx",
  "src/features/dashboard/components/PhaseProgressPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/index.ts",
  "src/app/page.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing dashboard skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "broker_client",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Dashboard skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_16_DASHBOARD_SKELETON_CONTRACT.md <<'EOF'
# Phase 16 Dashboard Skeleton Contract

Status: skeleton only.

Allowed:
- static dashboard panels
- stack overview placeholder
- system lock placeholder
- phase progress placeholder
- dashboard state contract
- dashboard verification

Forbidden:
- backend API calls
- broker calls
- market data calls
- AI calls
- runtime execution
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_16_DASHBOARD_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 16 Dashboard Skeleton Certification

Status: PASS

Verified:
- dashboard state exists
- dashboard shell exists
- system lock panel exists
- stack overview panel exists
- phase progress panel exists
- no backend calls
- no broker calls
- no AI calls
- no trading logic

Result:
- Phase 16 dashboard skeleton is certified.
EOF

git add .
git commit -m "Phase 16: Dashboard skeleton"

git tag -a phase-16-dashboard-skeleton \
  -m "Certified Phase 16 dashboard skeleton"

git push
git push --tags

echo "PASS: Phase 16 complete."
