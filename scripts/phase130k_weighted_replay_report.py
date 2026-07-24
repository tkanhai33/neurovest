#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
from collections import defaultdict, Counter

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"

runs = sorted([p for p in RUN_ROOT.glob("WEIGHTED_REPLAY_*") if p.is_dir()])
assert runs, "No weighted replay run found."

RUN = runs[-1]
LEDGER = RUN / "decision_ledger.jsonl"

stats = defaultdict(lambda: {
    "rows": 0,
    "reward_total": 0.0,
    "confidence_total": 0.0,
    "decisions": Counter(),
})

overall_decisions = Counter()

for line in LEDGER.open(encoding="utf-8"):
    if not line.strip():
        continue

    row = json.loads(line)

    symbol = row.get("symbol", "UNKNOWN")
    decision = row.get("decision", "UNKNOWN")
    reward = float(row.get("reward") or 0.0)
    confidence = float(row.get("confidence") or 0.0)

    s = stats[symbol]

    s["rows"] += 1
    s["reward_total"] += reward
    s["confidence_total"] += confidence
    s["decisions"][decision] += 1

    overall_decisions[decision] += 1

profiles = []

for symbol, s in stats.items():

    rows = max(1, s["rows"])

    profiles.append({

        "symbol": symbol,

        "rows": s["rows"],

        "reward_total": s["reward_total"],

        "average_reward": s["reward_total"] / rows,

        "average_confidence": s["confidence_total"] / rows,

        "decisions": dict(s["decisions"]),

    })

profiles.sort(key=lambda x: x["reward_total"], reverse=True)

report = {

    "phase": "130K_WEIGHTED_REPLAY_REPORT",

    "created_at": datetime.now(UTC).isoformat(),

    "run_directory": str(RUN),

    "profiles": profiles,

    "overall": {

        "rows": sum(x["rows"] for x in profiles),

        "decision_counts": dict(overall_decisions),

        "reward_total": sum(x["reward_total"] for x in profiles),

    },

    "certified": bool(profiles),

}

OUT_JSON = RUN / "130K_weighted_replay_report.json"
OUT_TXT = RUN / "130K_weighted_replay_report.txt"

OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [

    "130K_WEIGHTED_REPLAY_REPORT",
    "",
    f"certified: {report['certified']}",
    f"run: {RUN}",
    "",
    f"rows: {report['overall']['rows']}",
    f"reward_total: {report['overall']['reward_total']:.6f}",
    f"decisions: {report['overall']['decision_counts']}",
    "",
    "SYMBOL RESULTS",

]

for p in profiles:

    lines.append(

        f"{p['symbol']:<10} "
        f"rows={p['rows']:<6} "
        f"reward={p['reward_total']:.6f} "
        f"avg={p['average_reward']:.8f} "
        f"conf={p['average_confidence']:.4f} "
        f"decisions={p['decisions']}"

    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print()
print(OUT_TXT.read_text())
