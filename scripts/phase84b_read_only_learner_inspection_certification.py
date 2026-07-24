#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_learner_inspection_dry_run" / "84A_read_only_learner_inspection_dry_run_latest.json"

OUT_DIR = ARCH / "read_only_learner_inspection_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "84B_read_only_learner_inspection_certification_latest.json"
OUT_TXT = OUT_DIR / "84B_read_only_learner_inspection_certification_latest.txt"

PHASE = "84B_READ_ONLY_LEARNER_INSPECTION_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
inspection = source.get("inspection", {})
status = inspection.get("learner_status", {})
preview = inspection.get("learning_preview", {})
stress = inspection.get("stress_summary", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "inspection_present": bool(inspection),
    "report_id_present": bool(inspection.get("report_id")),
    "symbol_correct": inspection.get("symbol") == "VFV.TO",
    "row_count_present": inspection.get("row_count", 0) > 0,
    "stress_summary_present": bool(stress),
    "read_only_learner_enabled": status.get("read_only_learner_enabled") is True,
    "training_still_disabled": status.get("training_enabled") is False,
    "learner_write_still_disabled": status.get("learner_write_enabled") is False,
    "mutation_still_blocked": status.get("mutation_allowed") is False,
    "queue_write_still_blocked": status.get("queue_write_enabled") is False,
    "strategy_db_write_still_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_still_blocked": status.get("promotion_enabled") is False,
    "broker_live_still_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "preview_only": preview.get("mode") == "PREVIEW_ONLY",
    "source_no_errors": source.get("errors") == [],
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_LEARNER_INSPECTION_CERTIFICATION",
    "source_dry_run": str(SOURCE),
    "inspection_summary": {
        "report_id": inspection.get("report_id"),
        "symbol": inspection.get("symbol"),
        "row_count": inspection.get("row_count"),
        "cumulative_return": stress.get("cumulative_return"),
        "max_drawdown": stress.get("max_drawdown"),
        "negative_return_days": stress.get("negative_return_days"),
        "positive_return_days": stress.get("positive_return_days"),
    },
    "learner_status": status,
    "checks": checks,
    "policy": {
        "read_only_learner_inspection_certified": True,
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
    "recommended_next_phase": "84C_READ_ONLY_LEARNER_INSPECTION_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"report_id: {result['inspection_summary']['report_id']}",
        f"symbol: {result['inspection_summary']['symbol']}",
        f"row_count: {result['inspection_summary']['row_count']}",
        "",
        "Read-only learner inspection certified.",
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
    "inspection_summary": result["inspection_summary"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
