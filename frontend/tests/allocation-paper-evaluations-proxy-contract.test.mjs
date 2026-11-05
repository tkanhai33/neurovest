import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const route = readFileSync(
  process.argv[2],
  "utf8",
);

assert.match(
  route,
  /export async function GET\(\)/,
);

assert.match(
  route,
  /backendFetch/,
);

assert.match(
  route,
  /\/api\/v1\/strategy-library\/allocation-proposals\/paper-evaluations/,
);

assert.doesNotMatch(
  route,
  /export async function POST\(/,
);

assert.doesNotMatch(
  route,
  /export async function PUT\(/,
);

assert.doesNotMatch(
  route,
  /export async function DELETE\(/,
);

console.log("FRONTEND_PROXY_CONTRACT=PASS");
