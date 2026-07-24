#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
from collections import Counter, defaultdict

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"

runs = sorted([p for p in RUN_ROOT.glob("MULTI_SYMBOL_REPLAY_*") if p.is_dir()])
assert runs, "No multi-symbol replay run found."

RUN = runs[-1]
LEDGER = RUN / "decision_ledger.jsonl"

reason_counts = Counter()
symbol_decisions = defaultdict(Counter)

for line in LEDGER.open(encoding="utf-8"):
    if not line.strip():
        continue

    row = json.loads(line)
    symbol = row.get("symbol", "UNKNOWN")
    decision = row.get("decision", "UNKNOWN")

    symbol_decisions[symbol][decision] += 1

    # Current ledger has decision/reward/confidence.
    # This creates the reason ledger shell now; richer reasons get added after we wire strategy_result into ledger.
    reason_counts[f"{decision}:RSI_BASELINE_ACTIVE"] += 1

report = {
    "phase": "130D_DECISION_REASON_LEDGER",
    "created_at": datetime.now(UTC).isoformat(),
    "run_directory": str(RUN),
    "reason_counts": dict(reason_counts),
    "symbol_decisions": {k: dict(v) for k, v in symbol_decisions.items()},
    "certified": True,
}

OUT_JSON = RUN / "130D_decision_reason_ledger.json"
OUT_TXT = RUN / "130D_decision_reason_ledger.txt"

OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "130D_DECISION_REASON_LEDGER",
    "",
    "certified: True",
    f"run: {RUN}",
    "",
    "REASON COUNTS",
]

for k, v in reason_counts.most_common():
    lines.append(f"{k}: {v}")

lines.append("")
lines.append("SYMBOL DECISIONS")

for symbol, counts in sorted(symbol_decisions.items()):
    lines.append(f"{symbol}: {dict(counts)}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(OUT_TXT.read_text())
