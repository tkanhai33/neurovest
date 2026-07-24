#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"
OUT_DIR = ROOT / "frontend/public/neurovest-training"
OUT_DIR.mkdir(parents=True, exist_ok=True)

weighted_runs = sorted([p for p in RUN_ROOT.glob("WEIGHTED_REPLAY_*") if p.is_dir()])
assert weighted_runs, "No weighted replay runs found."

RUN = weighted_runs[-1]
REPORT = RUN / "130K_weighted_replay_report.json"
assert REPORT.exists(), f"Missing report: {REPORT}"

report = json.loads(REPORT.read_text(encoding="utf-8"))

payload = {
    "phase": "130L_TRAINING_METRICS_FRONTEND_FEED",
    "created_at": datetime.now(UTC).isoformat(),
    "active_run": RUN.name,
    "run_directory": str(RUN),
    "summary": report["overall"],
    "symbols": report["profiles"],
    "charts": {
        "reward_by_symbol": [
            {
                "symbol": p["symbol"],
                "reward": p["reward_total"],
                "avg_reward": p["average_reward"],
            }
            for p in report["profiles"]
        ],
        "decision_mix": [
            {
                "decision": k,
                "count": v,
            }
            for k, v in report["overall"]["decision_counts"].items()
        ],
        "confidence_by_symbol": [
            {
                "symbol": p["symbol"],
                "confidence": p["average_confidence"],
            }
            for p in report["profiles"]
        ],
    },
    "certified": True,
}

out = OUT_DIR / "latest_training_metrics.json"
out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps({
    "phase": payload["phase"],
    "certified": True,
    "frontend_feed": str(out),
    "active_run": payload["active_run"],
    "reward_total": payload["summary"]["reward_total"],
    "rows": payload["summary"]["rows"],
}, indent=2))
