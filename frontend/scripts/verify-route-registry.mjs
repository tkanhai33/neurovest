import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/lib/routes/routeRegistry.ts",
  "src/lib/routes/navigationState.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing route registry file: ${file}`);
}

const routeText = readFileSync("src/lib/routes/routeRegistry.ts", "utf8");

const expected = [
  "dashboard",
  "market_data",
  "portfolio",
  "research",
  "strategy",
  "risk",
  "paper_trading",
  "broker_integration",
  "runtime",
  "ai_chat",
  "admin_control",
  "settings"
];

for (const key of expected) {
  if (!routeText.includes(key)) {
    throw new Error(`Missing route key: ${key}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "broker_client"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Frontend route registry verified.");
