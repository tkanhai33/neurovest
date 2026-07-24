#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"
PUBLIC_DIR = ROOT / "frontend/public/neurovest-training"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

OUT = PUBLIC_DIR / "learning_state.json"

weighted_runs = sorted([p for p in RUN_ROOT.glob("WEIGHTED_REPLAY_*") if p.is_dir()])
assert weighted_runs, "No weighted replay runs found."

history = []
lifetime_rows = 0
lifetime_reward = 0.0
lifetime_decisions = {"BUY": 0, "SELL": 0, "HOLD": 0}

for run in weighted_runs:
    report_path = run / "130K_weighted_replay_report.json"
    if not report_path.exists():
        continue

    report = json.loads(report_path.read_text(encoding="utf-8"))
    overall = report.get("overall", {})

    decision_counts = overall.get("decision_counts", {})
    reward_total = float(overall.get("reward_total", 0.0))
    rows = int(overall.get("rows", 0))

    lifetime_rows += rows
    lifetime_reward += reward_total

    for k in lifetime_decisions:
        lifetime_decisions[k] += int(decision_counts.get(k, 0))

    history.append({
        "run_id": run.name,
        "rows": rows,
        "reward_total": reward_total,
        "decision_counts": decision_counts,
        "symbols": report.get("profiles", []),
    })

current = history[-1]

payload = {
    "phase": "130M_LEARNING_STATE_FEED",
    "created_at": datetime.now(UTC).isoformat(),
    "current_run": current,
    "lifetime": {
        "runs": len(history),
        "rows_processed": lifetime_rows,
        "reward_total": lifetime_reward,
        "decision_counts": lifetime_decisions,
    },
    "history": history,
    "charts": {
        "reward_history": [
            {"run_id": h["run_id"], "reward_total": h["reward_total"]}
            for h in history
        ],
        "rows_history": [
            {"run_id": h["run_id"], "rows": h["rows"]}
            for h in history
        ],
        "current_reward_by_symbol": [
            {
                "symbol": s["symbol"],
                "reward": s["reward_total"],
                "avg_reward": s["average_reward"],
            }
            for s in current["symbols"]
        ],
        "current_confidence_by_symbol": [
            {
                "symbol": s["symbol"],
                "confidence": s["average_confidence"],
            }
            for s in current["symbols"]
        ],
        "current_decision_mix": [
            {"decision": k, "count": v}
            for k, v in current["decision_counts"].items()
        ],
    },
    "certified": True,
}

OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps({
    "phase": payload["phase"],
    "certified": True,
    "out": str(OUT),
    "runs": payload["lifetime"]["runs"],
    "lifetime_rows": payload["lifetime"]["rows_processed"],
    "lifetime_reward": payload["lifetime"]["reward_total"],
}, indent=2))
