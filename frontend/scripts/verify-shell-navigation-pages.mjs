import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/app/page.tsx",
  "src/app/market-data/page.tsx",
  "src/app/portfolio/page.tsx",
  "src/app/research/page.tsx",
  "src/app/strategy/page.tsx",
  "src/app/risk/page.tsx",
  "src/app/paper-trading/page.tsx",
  "src/app/broker-integration/page.tsx",
  "src/app/runtime/page.tsx",
  "src/app/ai-chat/page.tsx",
  "src/app/admin/page.tsx",
  "src/app/settings/page.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing shell navigation page: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "useEffect(",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "ollama.chat",
  "ollama.generate",
  "setInterval",
  "setTimeout"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Shell navigation pages verified.");
