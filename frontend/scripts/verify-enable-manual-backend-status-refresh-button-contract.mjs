import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/backendStatusRefreshController.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx",
  "src/features/admin_control/client/backendStatusClient.ts"
];

const sourceFiles = required.filter(
  (file) =>
    file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing enable manual backend status refresh button contract file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "buttonShellOnly: false",
    "manualOnly: true",
    "readOnly: true",
    "clickFetchEnabled: true",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "actionShellOnly: false",
    "manualOnly: true",
    "readOnly: true",
    "uiFetchEnabled: true",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "manual_backend_status_refresh",
    "fetchBackendStatus.name"
  ],
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx": [
    "backendStatusRefreshButtonLabel",
    "backendStatusRefreshButtonState",
    "disabled"
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

console.log("PASS: Enable manual backend status refresh button contract verified.");
