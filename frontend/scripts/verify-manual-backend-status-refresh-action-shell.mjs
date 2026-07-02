import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/backendStatusRefreshState.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing manual backend status refresh action shell file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "actionShellOnly: false",
    "manualOnly: true",
    "readOnly: true",
    "autoFetchEnabled: false",
    "pollingEnabled: false",
    "intervalEnabled: false",
    "uiFetchEnabled: true",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "getBackendStatusRefreshActionLabel",
    "getBackendStatusRefreshActionContract",
    "manual_backend_status_refresh",
    "fetchBackendStatus.name"
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

const sourceFiles = required.filter(
  (file) => file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Manual backend status refresh action shell verified.");
