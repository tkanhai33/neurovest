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

stats = defaultdict(lambda: {
    "rows": 0,
    "reward_total": 0.0,
    "confidence_total": 0.0,
    "decisions": Counter(),
    "buy_reward": 0.0,
    "sell_reward": 0.0,
    "hold_reward": 0.0,
})

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

    if decision == "BUY":
        s["buy_reward"] += reward
    elif decision == "SELL":
        s["sell_reward"] += reward
    elif decision == "HOLD":
        s["hold_reward"] += reward

profiles = []

for symbol, s in stats.items():
    rows = max(1, s["rows"])
    trade_count = s["decisions"].get("BUY", 0) + s["decisions"].get("SELL", 0)
    trade_ratio = trade_count / rows
    avg_reward = s["reward_total"] / rows
    avg_confidence = s["confidence_total"] / rows

    if s["reward_total"] > 0:
        grade = "TRAIN_MORE"
    elif avg_reward > -0.00025:
        grade = "WATCHLIST"
    elif avg_reward > -0.00055:
        grade = "WEAK"
    else:
        grade = "TOXIC_FOR_CURRENT_STRATEGY"

    if trade_ratio > 0.75 and s["reward_total"] < 0:
        risk_note = "overtrading_negative_reward"
    elif s["reward_total"] > 0:
        risk_note = "positive_reward_candidate"
    else:
        risk_note = "needs_threshold_tuning"

    profiles.append({
        "symbol": symbol,
        "rows": s["rows"],
        "reward_total": s["reward_total"],
        "average_reward": avg_reward,
        "average_confidence": avg_confidence,
        "decisions": dict(s["decisions"]),
        "trade_ratio": trade_ratio,
        "buy_reward": s["buy_reward"],
        "sell_reward": s["sell_reward"],
        "hold_reward": s["hold_reward"],
        "grade": grade,
        "risk_note": risk_note,
    })

profiles.sort(key=lambda x: x["reward_total"], reverse=True)

report = {
    "phase": "130E_SYMBOL_INTELLIGENCE_REPORT",
    "created_at": datetime.now(UTC).isoformat(),
    "run_directory": str(RUN),
    "profiles": profiles,
    "train_more": [p["symbol"] for p in profiles if p["grade"] == "TRAIN_MORE"],
    "watchlist": [p["symbol"] for p in profiles if p["grade"] == "WATCHLIST"],
    "toxic": [p["symbol"] for p in profiles if p["grade"] == "TOXIC_FOR_CURRENT_STRATEGY"],
    "certified": bool(profiles),
}

OUT_JSON = RUN / "130E_symbol_intelligence_report.json"
OUT_TXT = RUN / "130E_symbol_intelligence_report.txt"

OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "130E_SYMBOL_INTELLIGENCE_REPORT",
    "",
    f"certified: {report['certified']}",
    f"run: {RUN}",
    "",
    f"TRAIN_MORE: {report['train_more']}",
    f"WATCHLIST: {report['watchlist']}",
    f"TOXIC: {report['toxic']}",
    "",
    "SYMBOL PROFILES",
]

for p in profiles:
    lines.append(
        f"{p['symbol']:<10} "
        f"grade={p['grade']:<27} "
        f"reward={p['reward_total']:.6f} "
        f"avg={p['average_reward']:.8f} "
        f"trade_ratio={p['trade_ratio']:.3f} "
        f"decisions={p['decisions']} "
        f"note={p['risk_note']}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(OUT_TXT.read_text())
