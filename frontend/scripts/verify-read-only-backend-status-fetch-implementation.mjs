import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/client/backendStatusClient.ts",
  "src/features/admin_control/contracts/backendStatusFetchContract.ts",
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status fetch implementation file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/client/backendStatusClient.ts": [
    "phase_38f_read_only_backend_status_fetch_implementation",
    "fetchImplementationEnabled: true",
    "manualFetchOnly: true",
    "uiFetchEnabled: false",
    "pollingEnabled: false",
    "backendCallsEnabled: true",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "fetchBackendStatus",
    "await fetch(",
    "method: backendStatusFetchContract.method"
  ]
};

for (const [file, terms] of Object.entries(requiredTerms)) {
  const text = readFileSync(file, "utf8");
  for (const term of terms) {
    if (!text.includes(term)) throw new Error(`Required term ${term} missing from ${file}`);
  }
}

const forbidden = [
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
  "setTimeout(",
  "POST",
  "PUT",
  "PATCH",
  "DELETE"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Read-only backend status fetch implementation verified.");
