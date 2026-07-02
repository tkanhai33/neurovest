import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/admin_control/view_model/backendStatusButtonClickHandler.ts",
  "src/features/admin_control/view_model/backendStatusRefreshController.ts",
  "src/features/admin_control/view_model/index.ts",
  "src/features/admin_control/client/backendStatusClient.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing backend status button click wiring shell file: ${file}`);
}

const requiredTerms = {
  "src/features/admin_control/view_model/backendStatusButtonClickHandler.ts": [
    "phase_38r_button_click_wiring_shell",
    "clickHandlerShellOnly: true",
    "manualOnly: true",
    "readOnly: true",
    "buttonClickWiringPrepared: true",
    "clickHandlerEnabled: false",
    "invokesFetch: false",
    "requestTransitionsEnabled: false",
    "uiFetchEnabled: false",
    "backendCallsEnabled: false",
    "runtimeEnabled: false",
    "brokerCallsEnabled: false",
    "tradingEnabled: false",
    "mutationEnabled: false",
    "getBackendStatusButtonClickPreview"
  ],
  "src/features/admin_control/view_model/index.ts": [
    "backendStatusButtonClickHandlerState",
    "getBackendStatusButtonClickPreview"
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

const sourceFiles = required.filter(
  (file) => file !== "src/features/admin_control/client/backendStatusClient.ts"
);

for (const file of sourceFiles) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Backend status button click wiring shell verified.");
