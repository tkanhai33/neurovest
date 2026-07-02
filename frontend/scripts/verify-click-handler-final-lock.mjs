import { existsSync, readFileSync } from "node:fs";

const file = "src/features/admin_control/view_model/backendStatusButtonClickHandler.ts";

if (!existsSync(file)) {
  throw new Error("missing handler");
}

const text = readFileSync(file, "utf8");

const required = [
  "phase_38v_click_handler_final_lock",
  "mutationLocked: true",
  "executionLocked: true",
  "fetchLocked: true",
  "controllerCouplingLocked: true"
];

for (const r of required) {
  if (!text.includes(r)) {
    throw new Error("missing: " + r);
  }
}

console.log("PASS: Phase 38V click handler locked");
