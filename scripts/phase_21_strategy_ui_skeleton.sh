#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 21 - STRATEGY UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/strategy/components" \
  "$FRONTEND/src/features/strategy/contracts"

cat > "$FRONTEND/src/features/strategy/contracts/strategyUiState.ts" <<'EOF'
export const strategyUiState = {
  phase: "phase_21_strategy_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  signalGenerationEnabled: false,
  scoringEnabled: false,
  promotionEnabled: false,
  tradingEnabled: false
} as const;

export const strategyModules = [
  "Signals",
  "Candidates",
  "Scoring",
  "Version Lineage",
  "Promotion Review"
] as const;
EOF

cat > "$FRONTEND/src/features/strategy/components/StrategyOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { strategyModules } from "../contracts/strategyUiState";

export function StrategyOverviewPanel() {
  return (
    <Card>
      <h2>Strategy Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {strategyModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/strategy/components/SignalPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function SignalPlaceholderPanel() {
  return (
    <Card>
      <h2>Signal Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Direction" value="Locked" />
        <MetricTile label="Confidence" value="Disabled" />
        <MetricTile label="Symbol" value="Placeholder" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/strategy/components/CandidatePlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function CandidatePlaceholderPanel() {
  return (
    <Card>
      <h2>Candidate Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Candidate scoring locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/strategy/components/VersionLineagePlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function VersionLineagePlaceholderPanel() {
  return (
    <Card>
      <h2>Version / Lineage Placeholder</h2>
      <p style={{ color: "var(--muted)" }}>
        Strategy versions, parent lineage, and promotion review are locked during the skeleton phase.
      </p>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/strategy/components/StrategyPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { CandidatePlaceholderPanel } from "./CandidatePlaceholderPanel";
import { SignalPlaceholderPanel } from "./SignalPlaceholderPanel";
import { StrategyOverviewPanel } from "./StrategyOverviewPanel";
import { VersionLineagePlaceholderPanel } from "./VersionLineagePlaceholderPanel";

export function StrategyPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Strategy"
        subtitle="Static strategy UI skeleton. Signals, scoring, promotion, risk, and trading integration are locked."
      />
      <StrategyOverviewPanel />
      <SignalPlaceholderPanel />
      <CandidatePlaceholderPanel />
      <VersionLineagePlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/strategy/components/index.ts" <<'EOF'
export { CandidatePlaceholderPanel } from "./CandidatePlaceholderPanel";
export { SignalPlaceholderPanel } from "./SignalPlaceholderPanel";
export { StrategyOverviewPanel } from "./StrategyOverviewPanel";
export { StrategyPanel } from "./StrategyPanel";
export { VersionLineagePlaceholderPanel } from "./VersionLineagePlaceholderPanel";
EOF

cat > "$FRONTEND/scripts/verify-strategy-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/strategy/contracts/strategyUiState.ts",
  "src/features/strategy/components/StrategyOverviewPanel.tsx",
  "src/features/strategy/components/SignalPlaceholderPanel.tsx",
  "src/features/strategy/components/CandidatePlaceholderPanel.tsx",
  "src/features/strategy/components/VersionLineagePlaceholderPanel.tsx",
  "src/features/strategy/components/StrategyPanel.tsx",
  "src/features/strategy/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing strategy UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "generate_signal",
  "score_candidate",
  "optimize_strategy",
  "risk_approved",
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

console.log("PASS: Strategy UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-strategy-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-research-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-portfolio-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-market-data-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_21_STRATEGY_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 21 Strategy UI Skeleton Contract

Status: skeleton only.

Allowed:
- static strategy overview
- signal placeholder
- candidate placeholder
- version/lineage placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- signal generation
- candidate scoring
- optimization
- risk approval
- paper trading
- broker calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_21_STRATEGY_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 21 Strategy UI Skeleton Certification

Status: PASS

Verified:
- strategy UI state exists
- strategy overview panel exists
- signal placeholder panel exists
- candidate placeholder panel exists
- version/lineage placeholder exists
- no backend calls
- no signal generation
- no scoring
- no trading logic

Result:
- Phase 21 strategy UI skeleton is certified.
EOF

git add .
git commit -m "Phase 21: Strategy UI skeleton"

git tag -a phase-21-strategy-ui-skeleton \
  -m "Certified Phase 21 strategy UI skeleton"

git push
git push --tags

echo "PASS: Phase 21 complete."
