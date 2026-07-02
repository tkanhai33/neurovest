import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts",
  "src/features/admin_control/contracts/backendStatusUiState.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status bridge file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts": [
    "phase_37e_read_only_backend_status_bridge_contract",
    "frontendOnly: true",
    "bridgeOnly: true",
    "endpointPath: \"/admin-control/backend-status\"",
    "method: \"GET\"",
    "readOnly: true",
    "fetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "BackendStatusBridgeResponse"
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

console.log("PASS: Backend status bridge contract verified.");
