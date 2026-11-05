import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const panel = readFileSync(
  process.argv[2],
  "utf8",
);

assert.match(
  panel,
  /Historical allocation proposal snapshots/,
);

assert.match(
  panel,
  /allocation-proposals\/paper-evaluations/,
);

assert.match(
  panel,
  /data-testid="dashboard-allocation-paper-evaluations"/,
);

assert.match(
  panel,
  /not[\s\S]*strategy backtests, forecasts, or trading instructions/,
);

assert.match(
  panel,
  /credentials: "include"/,
);

console.log("DASHBOARD_ALLOCATION_SNAPSHOTS_CONTRACT=PASS");
