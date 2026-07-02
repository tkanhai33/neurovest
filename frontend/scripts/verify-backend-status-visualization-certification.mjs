import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/contracts/backendStatusUiState.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx",
  "src/features/admin_control/components/index.ts",
  "src/features/dashboard/components/DashboardShell.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status visualization file: ${file}`);
}

const shell = readFileSync("src/features/dashboard/components/DashboardShell.tsx", "utf8");
if (!shell.includes("BackendStatusPreviewPanel")) {
  throw new Error("DashboardShell missing BackendStatusPreviewPanel");
}

const requiredTerms = {
  "src/features/admin_control/contracts/backendStatusUiState.ts": [
    "phase_37b_read_only_backend_status_frontend_contract_mirror",
    "frontendOnly: true",
    "readOnly: true",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false"
  ],
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx": [
    "Read-Only Backend Status",
    "Static frontend mirror",
    "No fetch",
    "backend call",
    "runtime execution",
    "broker call",
    "AI call",
    "provider call",
    "mutation",
    "trading path"
  ]
};

for (const [file, terms] of Object.entries(requiredTerms)) {
  const text = readFileSync(file, "utf8");
  for (const term of terms) {
    if (!text.includes(term)) throw new Error(`Required term ${term} missing from ${file}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "localStorage",
  "sessionStorage",
  "document.cookie",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "useEffect(",
  "setInterval(",
  "setTimeout("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Backend status visualization certified.");
