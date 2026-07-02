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
