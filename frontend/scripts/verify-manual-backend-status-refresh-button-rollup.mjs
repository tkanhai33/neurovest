import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRefreshState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx",
  "src/features/admin_control/client/backendStatusClient.ts",
  "scripts/verify-manual-backend-status-refresh-ui-shell.mjs",
  "scripts/verify-manual-backend-status-refresh-action-shell.mjs",
  "scripts/verify-manual-backend-status-refresh-rollup.mjs",
  "scripts/verify-manual-backend-status-refresh-button-shell.mjs"
];

const sourceFiles = required.filter(
  (file) =>
    !file.startsWith("scripts/") &&
    file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing manual backend status refresh button rollup file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRefreshButtonState.ts": [
    "phase_38k_manual_backend_status_refresh_button_shell",
    "buttonShellOnly: true",
    "manualOnly: true",
    "readOnly: true",
    "clickFetchEnabled: false",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "Refresh Backend Status"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts": [
    "phase_38i_manual_backend_status_refresh_action_shell",
    "actionShellOnly: true",
    "manualOnly: true",
    "backendCallsEnabled: false",
    "manual_backend_status_refresh"
  ],
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx": [
    "backendStatusRefreshButtonLabel",
    "backendStatusRefreshButtonState",
    "type=\"button\"",
    "disabled",
    "Button shell only"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusRefreshButtonLabel",
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

console.log("PASS: Manual backend status refresh button rollup certified.");
