import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const [
  panelPath,
  dashboardPath,
] = process.argv.slice(2);

const panel = readFileSync(
  panelPath,
  "utf8",
);

const dashboard = readFileSync(
  dashboardPath,
  "utf8",
);

assert.match(
  panel,
  /neurovest_strategy_paper_order_intent_v1/,
);

assert.match(
  panel,
  /neurovest:open-user-workspace-v1/,
);

assert.match(
  panel,
  /workspace: "orders"/,
);

assert.match(
  dashboard,
  /neurovest:open-user-workspace-v1/,
);

assert.match(
  dashboard,
  /setActiveWorkspace\("orders"\)/,
);

assert.doesNotMatch(
  panel,
  /api\/v1\/paper\/orders/,
);

console.log("DIRECT_PAPER_REVIEW_NAVIGATION_CONTRACT=PASS");
