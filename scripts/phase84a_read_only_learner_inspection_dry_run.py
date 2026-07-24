#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_learner_enablement_rollup" / "83H_read_only_learner_enablement_rollup_latest.json"
LEARNER = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py"
REPORT = ARCH / "stress_test_report_store/store/VFV_TO_stress_test_report_read_only.json"

OUT_DIR = ARCH / "read_only_learner_inspection_dry_run"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "84A_read_only_learner_inspection_dry_run_latest.json"
OUT_TXT = OUT_DIR / "84A_read_only_learner_inspection_dry_run_latest.txt"

PHASE = "84A_READ_ONLY_LEARNER_INSPECTION_DRY_RUN"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("training_read_only_learner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
report = read_json(REPORT)

errors = []
inspection = {}

try:
    learner = import_file(LEARNER)
    status = learner.learner_status()

    inspection = {
        "mode": "READ_ONLY_INSPECTION_DRY_RUN",
        "learner_status": status,
        "report_id": report.get("report_id"),
        "symbol": report.get("symbol"),
        "row_count": report.get("row_count"),
        "stress_summary": report.get("stress_tests", {}),
        "learning_preview": learner.preview_learning_input(
            report.get("report_id", "UNKNOWN_REPORT"),
            "INACTIVE_DRAFT_FIXTURE_0001",
        ),
    }

except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

status = inspection.get("learner_status", {})
preview = inspection.get("learning_preview", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "learner_exists": LEARNER.exists(),
    "report_exists": REPORT.exists(),
    "inspection_present": bool(inspection),
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
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_LEARNER_INSPECTION_DRY_RUN",
    "source_rollup": str(SOURCE),
    "learner_file": str(LEARNER),
    "report_file": str(REPORT),
    "inspection": inspection,
    "errors": errors,
    "checks": checks,
    "policy": {
        "read_only_learner_inspection_dry_run_certified": True,
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
    "recommended_next_phase": "84B_READ_ONLY_LEARNER_INSPECTION_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"report_id: {inspection.get('report_id')}",
        f"symbol: {inspection.get('symbol')}",
        f"row_count: {inspection.get('row_count')}",
        "",
        "Read-only learner inspected report only.",
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
    "report_id": inspection.get("report_id"),
    "symbol": inspection.get("symbol"),
    "row_count": inspection.get("row_count"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "errors": errors,
}, indent=2))
