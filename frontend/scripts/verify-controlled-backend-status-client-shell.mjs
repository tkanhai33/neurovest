import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/client/backendStatusClient.ts",
  "src/features/admin_control/client/index.ts",
  "src/features/admin_control/contracts/backendStatusFetchContract.ts",
  "src/features/admin_control/contracts/backendStatusBridgeContract.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status client shell file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/client/backendStatusClient.ts": [
    "phase_38b_controlled_backend_status_client_shell",
    "clientShellOnly: true",
    "readOnly: true",
    "fetchImplementationEnabled: false",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "getBackendStatusClientContract",
    "BackendStatusClientResponse"
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

console.log("PASS: Controlled backend status client shell verified.");
