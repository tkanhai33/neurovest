import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/components/ui/Button.tsx",
  "src/components/ui/Card.tsx",
  "src/components/ui/Badge.tsx",
  "src/components/ui/StatusPill.tsx",
  "src/components/ui/PageHeader.tsx",
  "src/components/ui/SectionPanel.tsx",
  "src/components/ui/MetricTile.tsx",
  "src/components/ui/index.ts",
  "src/lib/contracts/designSystemState.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing design system file: ${file}`);
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

console.log("PASS: Design system skeleton verified.");
