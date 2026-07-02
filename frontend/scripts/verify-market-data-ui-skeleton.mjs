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
  "import yfinance",
  "import finnhub",
  "requests.get",
  "httpx.get",
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
