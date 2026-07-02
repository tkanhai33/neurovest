import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/contracts/dashboardState.ts",
  "src/features/dashboard/components/SystemLockPanel.tsx",
  "src/features/dashboard/components/StackOverviewPanel.tsx",
  "src/features/dashboard/components/PhaseProgressPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/index.ts",
  "src/app/page.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing dashboard skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
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

console.log("PASS: Dashboard skeleton verified.");
