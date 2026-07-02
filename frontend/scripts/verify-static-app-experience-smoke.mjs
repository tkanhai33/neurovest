import { existsSync, readFileSync } from "node:fs";

const routes = [
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

for (const route of routes) {
  if (!existsSync(route)) throw new Error(`Missing static app route: ${route}`);
}

const requiredShell = [
  "src/layouts/AppShell.tsx",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/styles/theme.css",
  "src/lib/routes/routeRegistry.ts",
  "src/lib/integration/featureIntegrationRegistry.ts"
];

for (const file of requiredShell) {
  if (!existsSync(file)) throw new Error(`Missing shell file: ${file}`);
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
  "setTimeout",
  "access_token",
  "refresh_token"
];

for (const file of [...routes, ...requiredShell]) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Static app experience smoke verified.");
