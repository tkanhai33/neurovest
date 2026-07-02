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
