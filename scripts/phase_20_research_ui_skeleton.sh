#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 20 - RESEARCH UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/research/components" \
  "$FRONTEND/src/features/research/contracts"

cat > "$FRONTEND/src/features/research/contracts/researchUiState.ts" <<'EOF'
export const researchUiState = {
  phase: "phase_20_research_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  marketDataCallsEnabled: false,
  aiCallsEnabled: false,
  strategyGenerationEnabled: false,
  tradingEnabled: false
} as const;

export const researchModules = [
  "Indicators",
  "Screeners",
  "Backtests",
  "News Summary",
  "Historical Comparison"
] as const;
EOF

cat > "$FRONTEND/src/features/research/components/ResearchOverviewPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { researchModules } from "../contracts/researchUiState";

export function ResearchOverviewPanel() {
  return (
    <Card>
      <h2>Research Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {researchModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/IndicatorPlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function IndicatorPlaceholderPanel() {
  return (
    <Card>
      <h2>Indicator Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="RSI" value="Locked" />
        <MetricTile label="MACD" value="Locked" />
        <MetricTile label="EMA" value="Locked" />
        <MetricTile label="ATR" value="Locked" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/ScreenerPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function ScreenerPlaceholderPanel() {
  return (
    <Card>
      <h2>Screener Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Screener locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/BacktestPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function BacktestPlaceholderPanel() {
  return (
    <Card>
      <h2>Backtest Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Backtest execution locked
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/NewsResearchPlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function NewsResearchPlaceholderPanel() {
  return (
    <Card>
      <h2>News / Research Placeholder</h2>
      <p style={{ color: "var(--muted)" }}>
        News ingestion, summaries, and AI analysis are locked during the skeleton phase.
      </p>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/ResearchPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { BacktestPlaceholderPanel } from "./BacktestPlaceholderPanel";
import { IndicatorPlaceholderPanel } from "./IndicatorPlaceholderPanel";
import { NewsResearchPlaceholderPanel } from "./NewsResearchPlaceholderPanel";
import { ResearchOverviewPanel } from "./ResearchOverviewPanel";
import { ScreenerPlaceholderPanel } from "./ScreenerPlaceholderPanel";

export function ResearchPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Research"
        subtitle="Static research UI skeleton. Calculations, screeners, backtests, news calls, and AI analysis are locked."
      />
      <ResearchOverviewPanel />
      <IndicatorPlaceholderPanel />
      <ScreenerPlaceholderPanel />
      <BacktestPlaceholderPanel />
      <NewsResearchPlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/research/components/index.ts" <<'EOF'
export { BacktestPlaceholderPanel } from "./BacktestPlaceholderPanel";
export { IndicatorPlaceholderPanel } from "./IndicatorPlaceholderPanel";
export { NewsResearchPlaceholderPanel } from "./NewsResearchPlaceholderPanel";
export { ResearchOverviewPanel } from "./ResearchOverviewPanel";
export { ResearchPanel } from "./ResearchPanel";
export { ScreenerPlaceholderPanel } from "./ScreenerPlaceholderPanel";
EOF

cat > "$FRONTEND/scripts/verify-research-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/research/contracts/researchUiState.ts",
  "src/features/research/components/ResearchOverviewPanel.tsx",
  "src/features/research/components/IndicatorPlaceholderPanel.tsx",
  "src/features/research/components/ScreenerPlaceholderPanel.tsx",
  "src/features/research/components/BacktestPlaceholderPanel.tsx",
  "src/features/research/components/NewsResearchPlaceholderPanel.tsx",
  "src/features/research/components/ResearchPanel.tsx",
  "src/features/research/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing research UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "calculate_rsi",
  "calculate_macd",
  "run_backtest",
  "generate_signal",
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

console.log("PASS: Research UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-research-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-portfolio-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-market-data-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_20_RESEARCH_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 20 Research UI Skeleton Contract

Status: skeleton only.

Allowed:
- static research overview
- indicator placeholder
- screener placeholder
- backtest placeholder
- news/research placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- market data calls
- indicator calculations
- screener implementation
- backtest execution
- AI analysis
- strategy generation
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_20_RESEARCH_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 20 Research UI Skeleton Certification

Status: PASS

Verified:
- research UI state exists
- research overview panel exists
- indicator placeholder panel exists
- screener placeholder panel exists
- backtest placeholder panel exists
- news/research placeholder panel exists
- no backend calls
- no calculations
- no AI calls
- no trading logic

Result:
- Phase 20 research UI skeleton is certified.
EOF

git add .
git commit -m "Phase 20: Research UI skeleton"

git tag -a phase-20-research-ui-skeleton \
  -m "Certified Phase 20 research UI skeleton"

git push
git push --tags

echo "PASS: Phase 20 complete."
