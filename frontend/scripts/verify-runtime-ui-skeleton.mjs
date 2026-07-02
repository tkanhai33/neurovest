import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/runtime/contracts/runtimeUiState.ts",
  "src/features/runtime/components/RuntimeOverviewPanel.tsx",
  "src/features/runtime/components/RuntimeStatusPanel.tsx",
  "src/features/runtime/components/SchedulerLockedPanel.tsx",
  "src/features/runtime/components/WorkflowPlaceholderPanel.tsx",
  "src/features/runtime/components/EventLogPlaceholderPanel.tsx",
  "src/features/runtime/components/MutationLockedPanel.tsx",
  "src/features/runtime/components/RuntimePanel.tsx",
  "src/features/runtime/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing runtime UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "while True",
  "setInterval",
  "setTimeout",
  "execute_workflow",
  "run_scheduler",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "mutate_strategy",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Runtime UI skeleton verified.");
