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
