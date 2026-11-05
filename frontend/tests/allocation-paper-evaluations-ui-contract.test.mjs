import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const [pagePath, servicePath] = process.argv.slice(2);

const page = readFileSync(pagePath, "utf8");
const service = readFileSync(servicePath, "utf8");

assert.match(
  service,
  /fetchAllocationPaperEvaluations/,
);

assert.match(
  service,
  /allocation-proposals\/paper-evaluations/,
);

assert.match(
  page,
  /Historical proposal snapshots/,
);

assert.match(
  page,
  /not strategy backtests, forecasts, or trading instructions/,
);

assert.match(
  page,
  /data-testid="allocation-paper-evaluations"/,
);

assert.match(
  page,
  /credentials: "include"/,
);

console.log("ALLOCATION_PAPER_EVALUATIONS_UI_CONTRACT=PASS");
