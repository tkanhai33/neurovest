import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusButtonClickHandler.ts",
  "src/features/admin_control/view_model/backendStatusRefreshController.ts",
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/backendStatusRequestState.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts",
  "scripts/verify-backend-status-button-click-wiring-shell.mjs",
  "scripts/verify-enable-manual-backend-status-refresh-button-contract.mjs",
  "scripts/verify-manual-backend-status-refresh-controller-rollup.mjs",
  "scripts/verify-backend-status-refresh-request-state-rollup.mjs",
  "scripts/verify-read-only-backend-status-fetch-rollup.mjs"
];

const sourceFiles = required.filter(
  (file) =>
    !file.startsWith("scripts/") &&
    file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status button click wiring rollup file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusButtonClickHandler.ts": [
    "phase_38r_button_click_wiring_shell",
    "clickHandlerShellOnly: true",
    "buttonClickWiringPrepared: true",
    "clickHandlerEnabled: false",
    "invokesFetch: false",
    "requestTransitionsEnabled: false",
    "backendCallsEnabled: false",
    "getBackendStatusButtonClickPreview"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "buttonShellOnly: false",
    "clickFetchEnabled: true",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "actionShellOnly: false",
    "uiFetchEnabled: true",
    "backendCallsEnabled: false",
    "manual_backend_status_refresh"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshController.ts": [
    "phase_38o_manual_backend_status_refresh_request_controller_shell",
    "controllerShellOnly: true",
    "buttonEnabled: false",
    "requestTransitionsEnabled: false",
    "backendCallsEnabled: false"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusButtonClickHandlerState",
    "getBackendStatusButtonClickPreview",
    "backendStatusRefreshControllerState",
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
  "await fetch(",
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

console.log("PASS: Backend status button click wiring rollup certified.");
