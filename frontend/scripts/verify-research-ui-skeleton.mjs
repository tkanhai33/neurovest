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
