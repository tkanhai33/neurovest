import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/app/page.tsx",
  "src/app/layout.tsx",
  "src/layouts/AppShell.tsx",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/components/FeatureCard.tsx",
  "src/lib/api/client.ts",
  "src/lib/contracts/frontendSystemState.ts",
  "src/styles/theme.css"
];

for (const file of required) {
  if (!existsSync(file)) {
    throw new Error(`Missing required frontend skeleton file: ${file}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "ollama.generate",
  "broker_client"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) {
      throw new Error(`Forbidden frontend term ${term} found in ${file}`);
    }
  }
}

console.log("PASS: Frontend skeleton verified.");
