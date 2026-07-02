import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/components/DashboardHeroPanel.tsx",
  "src/features/dashboard/components/CommandGridPanel.tsx",
  "src/features/dashboard/components/SystemLockPanel.tsx",
  "src/features/dashboard/components/StackOverviewPanel.tsx",
  "src/features/dashboard/components/PhaseProgressPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing dashboard visual composition file: ${file}`);
}

const shell = readFileSync("src/features/dashboard/components/DashboardShell.tsx", "utf8");

const expected = [
  "DashboardHeroPanel",
  "CommandGridPanel",
  "PhaseProgressPanel",
  "SystemLockPanel",
  "StackOverviewPanel"
];

for (const item of expected) {
  if (!shell.includes(item)) throw new Error(`Missing dashboard composition item: ${item}`);
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

console.log("PASS: Dashboard visual composition verified.");
