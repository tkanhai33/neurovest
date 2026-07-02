import { existsSync, readFileSync } from "node:fs";

const file = "src/features/admin_control/view_model/backendStatusClickControllerBridge.ts";

if (!existsSync(file)) {
  throw new Error("Missing click-controller bridge");
}

const text = readFileSync(file, "utf8");

const required = [
  "phase_38u_click_controller_preview_bridge",
  "bridgeOnly: true",
  "clickToControllerConnected: true",
  "executionEnabled: false",
  "backendMutationAllowed: false",
  "fetchAllowed: false"
];

for (const r of required) {
  if (!text.includes(r)) {
    throw new Error("Missing term: " + r);
  }
}

console.log("PASS: Phase 38U bridge verified");
