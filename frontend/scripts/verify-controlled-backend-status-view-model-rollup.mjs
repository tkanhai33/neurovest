import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/contracts/backendStatusFetchContract.ts",
  "src/features/admin_control/client/backendStatusClient.ts",
  "src/features/admin_control/client/index.ts",
  "src/features/admin_control/view_model/backendStatusViewModel.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx",
  "scripts/verify-controlled-backend-status-fetch-contract.mjs",
  "scripts/verify-controlled-backend-status-client-shell.mjs",
  "scripts/verify-controlled-backend-status-view-model-shell.mjs",
  "scripts/verify-backend-status-panel-view-model.mjs"
];

const sourceFiles = required.filter((file) => !file.startsWith("scripts/") && file !== "src/features/admin_control/client/backendStatusClient.ts");

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing controlled backend status view model rollup file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/contracts/backendStatusFetchContract.ts": [
    "phase_38a_controlled_real_backend_status_fetch_contract",
    "fetchImplementationEnabled: false",
    "uiFetchEnabled: false"
  ],
  "src/features/admin_control/client/backendStatusClient.ts": [
    "phase_38f_read_only_backend_status_fetch_implementation",
    "clientShellOnly: false",
    "fetchImplementationEnabled: true"
  ],
  "src/features/admin_control/view_model/backendStatusViewModel.ts": [
    "phase_38c_controlled_backend_status_view_model_shell",
    "viewModelOnly: true",
    "usesPreviewStateOnly: true",
    "backendStatusDisplayModel"
  ],
  "src/features/admin_control/components/BackendStatusPreviewPanel.tsx": [
    "backendStatusDisplayModel",
    "backendStatusViewModelState",
    "Static frontend mirror",
    "Static frontend view model",
    "No fetch"
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

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Controlled backend status view model rollup certified.");
