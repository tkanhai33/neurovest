import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/contracts/backendStatusUiState.ts",
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "scripts/verify-backend-status-frontend-mirror.mjs",
  "scripts/verify-backend-status-visualization-certification.mjs",
  "scripts/verify-backend-status-bridge-contract.mjs",
  "scripts/verify-backend-status-bridge-certification.mjs",
  "scripts/verify-read-only-backend-status-bridge-rollup.mjs",
  "scripts/verify-backend-status-bridge-completion.mjs"
];

const sourceFiles = required.filter((f) => !f.startsWith("scripts/"));

for (const file of required) {
  if (!existsSync(file)) {
    throw new Error(`Missing Stage 1 artifact: ${file}`);
  }
}

const requiredTerms = {
  "src/features/admin_control/contracts/backendStatusUiState.ts": [
    "frontendOnly: true",
    "readOnly: true",
    "backendCallsEnabled: false"
  ],
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts": [
    "bridgeOnly: true",
    "fetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false"
  ],
  "src/features/dashboard/components/DashboardShell.tsx": [
    "BackendStatusPreviewPanel"
  ]
};

for (const [file, terms] of Object.entries(requiredTerms)) {
  const text = readFileSync(file, "utf8");
  for (const term of terms) {
    if (!text.includes(term)) {
      throw new Error(`Required term ${term} missing from ${file}`);
    }
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client"
];

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) {
      throw new Error(`Forbidden term ${term} found in ${file}`);
    }
  }
}

console.log("PASS: Stage 1 read-only observability complete.");
