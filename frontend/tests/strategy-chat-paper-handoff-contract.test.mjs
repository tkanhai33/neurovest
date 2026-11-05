import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const [
  strategyPath,
  paperPath,
  chatPath,
] = process.argv.slice(2);

const strategy = readFileSync(
  strategyPath,
  "utf8",
);

const paper = readFileSync(
  paperPath,
  "utf8",
);

const chat = readFileSync(
  chatPath,
  "utf8",
);

assert.match(
  strategy,
  /Explain in Neuro/,
);

assert.match(
  strategy,
  /Prepare simulated/,
);

assert.match(
  strategy,
  /neurovest:strategy-explanation-draft/,
);

assert.match(
  strategy,
  /neurovest_strategy_paper_order_intent_v1/,
);

assert.doesNotMatch(
  strategy,
  /api\/v1\/paper\/orders/,
);

assert.match(
  paper,
  /neurovest_strategy_paper_order_intent_v1/,
);

assert.match(
  paper,
  /setConfirmation\(false\)/,
);

assert.match(
  chat,
  /neurovest:strategy-explanation-draft/,
);

assert.match(
  chat,
  /setOpen\(true\)/,
);

console.log("STRATEGY_CHAT_PAPER_HANDOFF_CONTRACT=PASS");
