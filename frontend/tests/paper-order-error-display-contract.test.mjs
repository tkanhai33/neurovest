import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const panel = readFileSync(
  process.argv[2],
  "utf8",
);

assert.match(
  panel,
  /function formatPaperOrderError/,
);

assert.match(
  panel,
  /"message",\n      "reason"/,
);

assert.match(
  panel,
  /formatPaperOrderError\(\n            payload/,
);

assert.doesNotMatch(
  panel,
  /payload\.detail \?\?\n          payload\.error/,
);

console.log("PAPER_ORDER_ERROR_DISPLAY_CONTRACT=PASS");
