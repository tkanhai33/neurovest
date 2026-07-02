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
