import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/lib/integration/featureIntegrationRegistry.ts",
  "src/components/Sidebar.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing frontend integration file: ${file}`);
}

const registryText = readFileSync("src/lib/integration/featureIntegrationRegistry.ts", "utf8");

const expected = [
  "DashboardShell",
  "MarketDataPanel",
  "PortfolioPanel",
  "ResearchPanel",
  "StrategyPanel",
  "RiskPanel",
  "PaperTradingPanel",
  "BrokerIntegrationPanel",
  "RuntimePanel",
  "NeuroChatPanel"
];

for (const item of expected) {
  if (!registryText.includes(item)) {
    throw new Error(`Missing integrated feature: ${item}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "ollama.chat",
  "ollama.generate",
  "setInterval",
  "setTimeout",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Frontend integration registry verified.");
