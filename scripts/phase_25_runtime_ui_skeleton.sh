#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 25 - RUNTIME UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/runtime/components" \
  "$FRONTEND/src/features/runtime/contracts"

cat > "$FRONTEND/src/features/runtime/contracts/runtimeUiState.ts" <<'EOF'
export const runtimeUiState = {
  phase: "phase_25_runtime_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  schedulerEnabled: false,
  backgroundLoopsEnabled: false,
  workflowExecutionEnabled: false,
  mutationEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const runtimeModules = [
  "Runtime Status",
  "Scheduler Locked",
  "Workflow Placeholder",
  "Event Log Placeholder",
  "Mutation Locked"
] as const;
EOF

cat > "$FRONTEND/src/features/runtime/components/RuntimeOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { runtimeModules } from "../contracts/runtimeUiState";

export function RuntimeOverviewPanel() {
  return (
    <Card>
      <h2>Runtime Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {runtimeModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/RuntimeStatusPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function RuntimeStatusPanel() {
  return (
    <Card>
      <h2>Runtime Status</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Runtime" value="Locked" />
        <MetricTile label="Scheduler" value="Disabled" />
        <MetricTile label="Loops" value="Disabled" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/SchedulerLockedPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function SchedulerLockedPanel() {
  return (
    <Card>
      <h2>Scheduler Locked</h2>
      <StatusPill label="No Background Loops" />
      <StatusPill label="No Scheduled Jobs" />
      <StatusPill label="No Runtime Execution" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/WorkflowPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function WorkflowPlaceholderPanel() {
  return (
    <Card>
      <h2>Workflow Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Workflow execution locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/EventLogPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function EventLogPlaceholderPanel() {
  return (
    <Card>
      <h2>Event Log Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Runtime events unavailable until implementation phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/MutationLockedPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function MutationLockedPanel() {
  return (
    <Card>
      <h2>Mutation Locked</h2>
      <StatusPill label="AI Mutation Disabled" />
      <StatusPill label="Strategy Mutation Disabled" />
      <StatusPill label="Runtime Mutation Disabled" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/RuntimePanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { EventLogPlaceholderPanel } from "./EventLogPlaceholderPanel";
import { MutationLockedPanel } from "./MutationLockedPanel";
import { RuntimeOverviewPanel } from "./RuntimeOverviewPanel";
import { RuntimeStatusPanel } from "./RuntimeStatusPanel";
import { SchedulerLockedPanel } from "./SchedulerLockedPanel";
import { WorkflowPlaceholderPanel } from "./WorkflowPlaceholderPanel";

export function RuntimePanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Runtime"
        subtitle="Static runtime UI skeleton. Scheduler, loops, workflows, mutation, broker, and trading paths are locked."
      />
      <RuntimeOverviewPanel />
      <RuntimeStatusPanel />
      <SchedulerLockedPanel />
      <WorkflowPlaceholderPanel />
      <EventLogPlaceholderPanel />
      <MutationLockedPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/runtime/components/index.ts" <<'EOF'
export { EventLogPlaceholderPanel } from "./EventLogPlaceholderPanel";
export { MutationLockedPanel } from "./MutationLockedPanel";
export { RuntimeOverviewPanel } from "./RuntimeOverviewPanel";
export { RuntimePanel } from "./RuntimePanel";
export { RuntimeStatusPanel } from "./RuntimeStatusPanel";
export { SchedulerLockedPanel } from "./SchedulerLockedPanel";
export { WorkflowPlaceholderPanel } from "./WorkflowPlaceholderPanel";
EOF

cat > "$FRONTEND/scripts/verify-runtime-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/runtime/contracts/runtimeUiState.ts",
  "src/features/runtime/components/RuntimeOverviewPanel.tsx",
  "src/features/runtime/components/RuntimeStatusPanel.tsx",
  "src/features/runtime/components/SchedulerLockedPanel.tsx",
  "src/features/runtime/components/WorkflowPlaceholderPanel.tsx",
  "src/features/runtime/components/EventLogPlaceholderPanel.tsx",
  "src/features/runtime/components/MutationLockedPanel.tsx",
  "src/features/runtime/components/RuntimePanel.tsx",
  "src/features/runtime/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing runtime UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "while True",
  "setInterval",
  "setTimeout",
  "execute_workflow",
  "run_scheduler",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "mutate_strategy",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Runtime UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-runtime-ui-skeleton.mjs)
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

cat > docs/contracts/PHASE_25_RUNTIME_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 25 Runtime UI Skeleton Contract

Status: skeleton only.

Allowed:
- static runtime overview
- runtime status placeholder
- scheduler locked panel
- workflow placeholder
- event log placeholder
- mutation locked panel
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- scheduler implementation
- background loops
- workflow execution
- runtime mutation
- broker calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_25_RUNTIME_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 25 Runtime UI Skeleton Certification

Status: PASS

Verified:
- runtime UI state exists
- runtime overview panel exists
- runtime status panel exists
- scheduler locked panel exists
- workflow placeholder exists
- event log placeholder exists
- mutation locked panel exists
- no backend calls
- no scheduler logic
- no workflow execution
- no mutation logic
- no trading logic

Result:
- Phase 25 runtime UI skeleton is certified.
EOF

git add .
git commit -m "Phase 25: Runtime UI skeleton"

git tag -a phase-25-runtime-ui-skeleton \
  -m "Certified Phase 25 runtime UI skeleton"

git push
git push --tags

echo "PASS: Phase 25 complete."
