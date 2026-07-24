#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_replay_calculator_rollup" / "70D_fixture_replay_calculator_rollup_latest.json"
CALCULATOR = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py"
FIXTURE = ARCH / "fixture_bar_dataset" / "data" / "fixture_ohlcv_v1.csv"

OUT_DIR = ARCH / "single_fixture_replay_dry_run"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "71A_single_fixture_replay_dry_run_only_latest.json"
OUT_TXT = OUT_DIR / "71A_single_fixture_replay_dry_run_only_latest.txt"

PHASE = "71A_SINGLE_FIXTURE_REPLAY_DRY_RUN_ONLY"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("fixture_replay_calculator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
metrics = {}

try:
    module = import_file(CALCULATOR)
    metrics = module.calculate_fixture_metrics(FIXTURE)
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

safety = metrics.get("safety", {}) if isinstance(metrics, dict) else {}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "calculator_exists": CALCULATOR.exists(),
    "fixture_exists": FIXTURE.exists(),
    "metrics_generated": bool(metrics),
    "dataset_id_correct": metrics.get("dataset_id") == "fixture_ohlcv_v1",
    "row_count_correct": metrics.get("row_count") == 10,
    "no_errors": len(errors) == 0,
    "strategy_replay_blocked": safety.get("strategy_execution_allowed") is False,
    "historical_replay_blocked": safety.get("historical_replay_allowed") is False,
    "runtime_execution_blocked": safety.get("replay_runtime_enabled") is False,
    "strategy_db_write_blocked": safety.get("strategy_db_write_allowed") is False,
    "promotion_blocked": safety.get("promotion_enabled") is False,
    "broker_live_blocked": (
        safety.get("broker_execution_enabled") is False
        and safety.get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "SINGLE_FIXTURE_REPLAY_DRY_RUN_ONLY",
    "source_rollup": str(SOURCE),
    "calculator": str(CALCULATOR),
    "fixture_csv": str(FIXTURE),
    "metrics": metrics,
    "errors": errors,
    "policy": {
        "single_fixture_metric_dry_run_allowed": True,
        "historical_replay_allowed_now": False,
        "strategy_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "71B_NO_WRITE_NO_PROMOTION_NO_BROKER_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"dataset_id: {metrics.get('dataset_id')}",
        f"row_count: {metrics.get('row_count')}",
        "",
        "Safety:",
        f"strategy_db_write_allowed: {safety.get('strategy_db_write_allowed')}",
        f"promotion_enabled: {safety.get('promotion_enabled')}",
        f"broker_execution_enabled: {safety.get('broker_execution_enabled')}",
        f"live_execution_enabled: {safety.get('live_execution_enabled')}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "dataset_id": metrics.get("dataset_id"),
    "row_count": metrics.get("row_count"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
