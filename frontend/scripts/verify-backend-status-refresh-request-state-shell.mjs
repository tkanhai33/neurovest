import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRequestState.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/client/backendStatusClient.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status request state shell file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRequestState.ts": [
    "phase_38m_backend_status_refresh_request_state_shell",
    "requestStateShellOnly: true",
    "status: \"idle\"",
    "loading: false",
    "success: false",
    "error: null",
    "readOnly: true",
    "manualOnly: true",
    "autoFetchEnabled: false",
    "pollingEnabled: false",
    "intervalEnabled: false",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "Idle",
    "Loading",
    "Success",
    "Error"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusRequestState",
    "backendStatusRequestStateLabels"
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
  "onClick=",
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

console.log("PASS: Backend status refresh request state shell verified.");
