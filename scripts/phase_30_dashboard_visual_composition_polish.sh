#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 30 - DASHBOARD VISUAL COMPOSITION POLISH"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

cat > "$FRONTEND/src/features/dashboard/components/DashboardHeroPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function DashboardHeroPanel() {
  return (
    <Card>
      <div style={{ display: "grid", gap: "14px" }}>
        <div>
          <h1 style={{ margin: 0 }}>NeuroVest Command Center</h1>
          <p className="nv-muted">
            Certified static frontend shell. Backend, provider, AI, runtime, broker, and trading paths remain locked.
          </p>
        </div>
        <div>
          <StatusPill label="Frontend Certified" />
          <StatusPill label="Runtime Locked" />
          <StatusPill label="Broker Locked" />
          <StatusPill label="Trading Locked" />
        </div>
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/CommandGridPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function CommandGridPanel() {
  return (
    <Card>
      <h2>Command Grid</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px" }}>
        <MetricTile label="Frontend Phases" value="13-30" />
        <MetricTile label="Backend Tests" value="85 Passing" />
        <MetricTile label="UI Surfaces" value="12" />
        <MetricTile label="Execution" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/SystemLockPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function SystemLockPanel() {
  return (
    <Card>
      <h2>System Locks</h2>
      <StatusPill label="Backend API Calls Locked" />
      <StatusPill label="Market Provider Calls Locked" />
      <StatusPill label="AI Model Calls Locked" />
      <StatusPill label="Runtime Execution Locked" />
      <StatusPill label="Broker Orders Locked" />
      <StatusPill label="Live Trading Locked" />
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
      <h2>Certified Stack Overview</h2>
      <p className="nv-muted">Every stack is present as a static locked shell.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {dashboardStacks.map((stack) => (
          <Badge key={stack} label={`${stack}: Certified Shell`} />
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
        <MetricTile label="Backend Topology" value="Certified" />
        <MetricTile label="Frontend Shell" value="Certified" />
        <MetricTile label="Visual Polish" value="Active" />
        <MetricTile label="API Wiring" value="Forbidden" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/DashboardShell.tsx" <<'EOF'
import { CommandGridPanel } from "./CommandGridPanel";
import { DashboardHeroPanel } from "./DashboardHeroPanel";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";

export function DashboardShell() {
  return (
    <div className="nv-grid">
      <DashboardHeroPanel />
      <CommandGridPanel />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/dashboard/components/index.ts" <<'EOF'
export { CommandGridPanel } from "./CommandGridPanel";
export { DashboardHeroPanel } from "./DashboardHeroPanel";
export { DashboardShell } from "./DashboardShell";
export { PhaseProgressPanel } from "./PhaseProgressPanel";
export { StackOverviewPanel } from "./StackOverviewPanel";
export { SystemLockPanel } from "./SystemLockPanel";
EOF

cat > "$FRONTEND/scripts/verify-dashboard-visual-composition.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/components/DashboardHeroPanel.tsx",
  "src/features/dashboard/components/CommandGridPanel.tsx",
  "src/features/dashboard/components/SystemLockPanel.tsx",
  "src/features/dashboard/components/StackOverviewPanel.tsx",
  "src/features/dashboard/components/PhaseProgressPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing dashboard visual composition file: ${file}`);
}

const shell = readFileSync("src/features/dashboard/components/DashboardShell.tsx", "utf8");

const expected = [
  "DashboardHeroPanel",
  "CommandGridPanel",
  "PhaseProgressPanel",
  "SystemLockPanel",
  "StackOverviewPanel"
];

for (const item of expected) {
  if (!shell.includes(item)) throw new Error(`Missing dashboard composition item: ${item}`);
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
  "setTimeout"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Dashboard visual composition verified.");
EOF

(
  cd "$FRONTEND"
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

cat > docs/contracts/PHASE_30_DASHBOARD_VISUAL_COMPOSITION_POLISH_CONTRACT.md <<'EOF'
# Phase 30 Dashboard Visual Composition Polish Contract

Status: visual polish only.

Allowed:
- dashboard hero composition
- dashboard command grid
- dashboard lock summary
- dashboard stack overview polish
- dashboard phase progress polish
- verification script
- certification artifact

Forbidden:
- backend API calls
- provider calls
- broker calls
- AI calls
- runtime execution
- scheduler logic
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_30_DASHBOARD_VISUAL_COMPOSITION_POLISH_CERTIFICATION.md <<'EOF'
# Phase 30 Dashboard Visual Composition Polish Certification

Status: PASS

Verified:
- dashboard hero panel exists
- command grid panel exists
- system lock panel polished
- stack overview panel polished
- phase progress panel polished
- dashboard shell composes polished panels
- no backend calls
- no provider calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic

Result:
- Phase 30 dashboard visual composition polish is certified.
EOF

git add .
git commit -m "Phase 30: Dashboard visual composition polish"

git tag -a phase-30-dashboard-visual-composition-polish \
  -m "Certified Phase 30 dashboard visual composition polish"

git push
git push --tags

echo "PASS: Phase 30 complete."
