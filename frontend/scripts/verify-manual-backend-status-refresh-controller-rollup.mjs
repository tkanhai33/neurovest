import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRefreshController.ts",
  "src/features/admin_control/view_model/backendStatusRequestState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshState.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts",
  "scripts/verify-manual-backend-status-refresh-controller-shell.mjs",
  "scripts/verify-backend-status-refresh-request-state-rollup.mjs",
  "scripts/verify-manual-backend-status-refresh-button-rollup.mjs",
  "scripts/verify-read-only-backend-status-fetch-rollup.mjs"
];

const sourceFiles = required.filter(
  (file) =>
    !file.startsWith("scripts/") &&
    file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing manual backend status refresh controller rollup file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRefreshController.ts": [
    "phase_38o_manual_backend_status_refresh_request_controller_shell",
    "controllerShellOnly: true",
    "manualOnly: true",
    "readOnly: true",
    "buttonEnabled: false",
    "requestTransitionsEnabled: false",
    "backendCallsEnabled: false",
    "getBackendStatusRefreshControllerPreview",
    "nextAllowedStates"
  ],
  "src/features/admin_control/view_model/backendStatusRequestState.ts": [
    "phase_38m_backend_status_refresh_request_state_shell",
    "status: \"idle\"",
    "loading: false",
    "success: false",
    "error: null"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusRefreshControllerState",
    "getBackendStatusRefreshControllerPreview",
    "backendStatusRequestState",
    "backendStatusRefreshButtonState",
    "backendStatusRefreshActionState"
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

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Manual backend status refresh controller rollup certified.");
