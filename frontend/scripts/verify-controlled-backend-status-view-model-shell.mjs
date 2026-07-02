import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusViewModel.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts",
  "src/features/admin_control/contracts/backendStatusUiState.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status view model shell file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusViewModel.ts": [
    "phase_38c_controlled_backend_status_view_model_shell",
    "viewModelOnly: true",
    "readOnly: true",
    "usesPreviewStateOnly: true",
    "fetchImplementationEnabled: false",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "providerCallsEnabled: false",
    "aiCallsEnabled: false",
    "backendStatusDisplayModel",
    "Client shell only"
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

const sourceFiles = required.filter((file) => file !== "src/features/admin_control/client/backendStatusClient.ts");

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Controlled backend status view model shell verified.");
