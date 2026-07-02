#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 18 - MARKET DATA UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/market_data/components" \
  "$FRONTEND/src/features/market_data/contracts"

cat > "$FRONTEND/src/features/market_data/contracts/marketDataUiState.ts" <<'EOF'
export const marketDataUiState = {
  phase: "phase_18_market_data_ui_skeleton",
  uiOnly: true,
  providerCallsEnabled: false,
  backendCallsEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const marketSymbols = [
  "RY.TO",
  "SHOP.TO",
  "VFV.TO",
  "VUN.TO",
  "BTC-CAD"
] as const;
EOF

cat > "$FRONTEND/src/features/market_data/components/ProviderStatusPanel.tsx" <<'EOF'
import { Card, StatusPill } from "../../../components/ui";

export function ProviderStatusPanel() {
  return (
    <Card>
      <h2>Provider Status</h2>
      <StatusPill label="yfinance Locked" />
      <StatusPill label="Finnhub Locked" />
      <StatusPill label="Backend Calls Locked" />
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/market_data/components/SymbolWatchlistPanel.tsx" <<'EOF'
import { Card, Badge } from "../../../components/ui";
import { marketSymbols } from "../contracts/marketDataUiState";

export function SymbolWatchlistPanel() {
  return (
    <Card>
      <h2>Symbol Watchlist</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {marketSymbols.map((symbol) => (
          <Badge key={symbol} label={`${symbol}: Placeholder`} />
        ))}
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/market_data/components/QuotePlaceholderPanel.tsx" <<'EOF'
import { Card, MetricTile } from "../../../components/ui";

export function QuotePlaceholderPanel() {
  return (
    <Card>
      <h2>Quote Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Last Price" value="Locked" />
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Provider" value="Disabled" />
        <MetricTile label="Freshness" value="No Calls" />
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/market_data/components/CandlePlaceholderPanel.tsx" <<'EOF'
import { Card } from "../../../components/ui";

export function CandlePlaceholderPanel() {
  return (
    <Card>
      <h2>Candle Chart Placeholder</h2>
      <div style={{ height: "180px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Chart locked during skeleton phase
      </div>
    </Card>
  );
}
EOF

cat > "$FRONTEND/src/features/market_data/components/MarketDataPanel.tsx" <<'EOF'
import { PageHeader } from "../../../components/ui";
import { CandlePlaceholderPanel } from "./CandlePlaceholderPanel";
import { ProviderStatusPanel } from "./ProviderStatusPanel";
import { QuotePlaceholderPanel } from "./QuotePlaceholderPanel";
import { SymbolWatchlistPanel } from "./SymbolWatchlistPanel";

export function MarketDataPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Market Data"
        subtitle="Static market data UI skeleton. Provider and backend calls are locked."
      />
      <ProviderStatusPanel />
      <SymbolWatchlistPanel />
      <QuotePlaceholderPanel />
      <CandlePlaceholderPanel />
    </div>
  );
}
EOF

cat > "$FRONTEND/src/features/market_data/components/index.ts" <<'EOF'
export { CandlePlaceholderPanel } from "./CandlePlaceholderPanel";
export { MarketDataPanel } from "./MarketDataPanel";
export { ProviderStatusPanel } from "./ProviderStatusPanel";
export { QuotePlaceholderPanel } from "./QuotePlaceholderPanel";
export { SymbolWatchlistPanel } from "./SymbolWatchlistPanel";
EOF

cat > "$FRONTEND/scripts/verify-market-data-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/market_data/contracts/marketDataUiState.ts",
  "src/features/market_data/components/ProviderStatusPanel.tsx",
  "src/features/market_data/components/SymbolWatchlistPanel.tsx",
  "src/features/market_data/components/QuotePlaceholderPanel.tsx",
  "src/features/market_data/components/CandlePlaceholderPanel.tsx",
  "src/features/market_data/components/MarketDataPanel.tsx",
  "src/features/market_data/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing market data UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "yfinance",
  "finnhub",
  "requests",
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

console.log("PASS: Market data UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-market-data-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_18_MARKET_DATA_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 18 Market Data UI Skeleton Contract

Status: skeleton only.

Allowed:
- static market data panel
- provider status placeholder
- symbol watchlist placeholder
- quote placeholder
- candle chart placeholder
- locked UI state contract
- verification script
- certification artifact

Forbidden:
- backend API calls
- real market data provider calls
- yfinance calls
- Finnhub calls
- broker calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_18_MARKET_DATA_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 18 Market Data UI Skeleton Certification

Status: PASS

Verified:
- market data UI state exists
- provider status panel exists
- symbol watchlist panel exists
- quote placeholder panel exists
- candle placeholder panel exists
- no backend calls
- no provider calls
- no broker calls
- no trading logic

Result:
- Phase 18 market data UI skeleton is certified.
EOF

git add .
git commit -m "Phase 18: Market data UI skeleton"

git tag -a phase-18-market-data-ui-skeleton \
  -m "Certified Phase 18 market data UI skeleton"

git push
git push --tags

echo "PASS: Phase 18 complete."
