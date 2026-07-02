import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusRefreshState.ts",
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts",
  "scripts/verify-manual-backend-status-refresh-ui-shell.mjs",
  "scripts/verify-manual-backend-status-refresh-action-shell.mjs",
  "scripts/verify-read-only-backend-status-fetch-rollup.mjs"
];

const sourceFiles = required.filter(
  (file) =>
    !file.startsWith("scripts/") &&
    file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing manual backend status refresh rollup file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusRefreshState.ts": [
    "phase_38h_manual_backend_status_refresh_ui_shell",
    "refreshShellOnly: true",
    "manualOnly: true",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false"
  ],
  "src/features/admin_control/view_model/backendStatusRefreshAction.ts": [
    "phase_38q_enable_manual_backend_status_refresh_button_contract",
    "actionShellOnly: false",
    "manualOnly: true",
    "readOnly: true",
    "uiFetchEnabled: true",
    "backendCallsEnabled: false",
    "manual_backend_status_refresh",
    "fetchBackendStatus.name"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusRefreshState",
    "backendStatusRefreshActionState",
    "getBackendStatusRefreshActionContract",
    "getBackendStatusRefreshActionLabel"
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

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Manual backend status refresh rollup certified.");
