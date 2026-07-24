#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
from collections import defaultdict, Counter

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"

runs = sorted([p for p in RUN_ROOT.glob("MULTI_SYMBOL_REPLAY_*") if p.is_dir()])
assert runs, "No multi-symbol replay run found."

RUN = runs[-1]
LEDGER = RUN / "decision_ledger.jsonl"

symbol_stats = defaultdict(lambda: {
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

    s = symbol_stats[symbol]
    s["rows"] += 1
    s["reward_total"] += reward
    s["confidence_total"] += confidence
    s["decisions"][decision] += 1
    overall_decisions[decision] += 1

symbol_report = []

for symbol, s in symbol_stats.items():
    rows = max(1, s["rows"])
    symbol_report.append({
        "symbol": symbol,
        "rows": s["rows"],
        "reward_total": s["reward_total"],
        "average_reward": s["reward_total"] / rows,
        "average_confidence": s["confidence_total"] / rows,
        "decisions": dict(s["decisions"]),
    })

symbol_report.sort(key=lambda x: x["reward_total"], reverse=True)

report = {
    "phase": "129H_MULTI_SYMBOL_REPLAY_REPORT",
    "created_at": datetime.now(UTC).isoformat(),
    "run_directory": str(RUN),
    "symbols": symbol_report,
    "overall": {
        "symbol_count": len(symbol_report),
        "rows": sum(s["rows"] for s in symbol_report),
        "decision_counts": dict(overall_decisions),
        "best_symbol": symbol_report[0] if symbol_report else None,
        "worst_symbol": symbol_report[-1] if symbol_report else None,
    },
    "certified": bool(symbol_report),
}

OUT_JSON = RUN / "129H_multi_symbol_replay_report.json"
OUT_TXT = RUN / "129H_multi_symbol_replay_report.txt"

OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "129H_MULTI_SYMBOL_REPLAY_REPORT",
    "",
    f"certified: {report['certified']}",
    f"run: {RUN}",
    "",
    "OVERALL",
    f"symbols: {report['overall']['symbol_count']}",
    f"rows: {report['overall']['rows']}",
    f"decisions: {report['overall']['decision_counts']}",
    "",
    "SYMBOL RANKING",
]

for s in symbol_report:
    lines.append(
        f"{s['symbol']:<10} rows={s['rows']:<6} "
        f"reward_total={s['reward_total']:.6f} "
        f"avg_reward={s['average_reward']:.8f} "
        f"avg_conf={s['average_confidence']:.4f} "
        f"decisions={s['decisions']}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": report["phase"],
    "certified": report["certified"],
    "run_directory": str(RUN),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "best_symbol": report["overall"]["best_symbol"]["symbol"] if report["overall"]["best_symbol"] else None,
    "worst_symbol": report["overall"]["worst_symbol"]["symbol"] if report["overall"]["worst_symbol"] else None,
}, indent=2))

print()
print(OUT_TXT.read_text())
