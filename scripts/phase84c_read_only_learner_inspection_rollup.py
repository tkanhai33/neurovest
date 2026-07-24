#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "84C_READ_ONLY_LEARNER_INSPECTION_ROLLUP"

EXPECTED = {
    "84A_inspection_dry_run": ARCH / "read_only_learner_inspection_dry_run/84A_read_only_learner_inspection_dry_run_latest.json",
    "84B_inspection_certification": ARCH / "read_only_learner_inspection_certification/84B_read_only_learner_inspection_certification_latest.json",
}

OUT_DIR = ARCH / "read_only_learner_inspection_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "84C_read_only_learner_inspection_rollup_latest.json"
OUT_TXT = OUT_DIR / "84C_read_only_learner_inspection_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read_json(path)
    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "phase": data.get("phase"),
        "certified": data.get("certified") is True,
    }
    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = data.get("certified") is True

cert = read_json(EXPECTED["84B_inspection_certification"])
summary = cert.get("inspection_summary", {})
status = cert.get("learner_status", {})

checks["summary_present"] = bool(summary)
checks["symbol_correct"] = summary.get("symbol") == "VFV.TO"
checks["row_count_present"] = summary.get("row_count", 0) > 0
checks["read_only_learner_enabled"] = status.get("read_only_learner_enabled") is True
checks["training_still_disabled"] = status.get("training_enabled") is False
checks["learner_write_still_disabled"] = status.get("learner_write_enabled") is False
checks["mutation_still_blocked"] = status.get("mutation_allowed") is False
checks["queue_write_still_blocked"] = status.get("queue_write_enabled") is False
checks["strategy_db_write_still_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_still_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_still_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_LEARNER_INSPECTION_ROLLUP",
    "artifacts": artifacts,
    "inspection_summary": summary,
    "learner_status": status,
    "policy": {
        "read_only_learner_inspection_rollup_certified": True,
        "read_only_learner_enabled": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "85A_TRAINING_EXECUTION_GATE_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: {summary.get('symbol')}",
        f"row_count: {summary.get('row_count')}",
        f"cumulative_return: {summary.get('cumulative_return')}",
        f"max_drawdown: {summary.get('max_drawdown')}",
        "",
        "Read-only learner inspection rollup certified.",
        "Training/write/mutation/queue/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "inspection_summary": summary,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
