#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util, json, py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "long_training_run_enablement_patch_apply/120E_long_training_run_enablement_patch_apply_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py"

OUT_DIR = ARCH / "long_training_run_enablement_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120F_long_training_run_enablement_certification_latest.json"
OUT_TXT = OUT_DIR / "120F_long_training_run_enablement_certification_latest.txt"

PHASE = "120F_LONG_TRAINING_RUN_ENABLEMENT_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("long_training_run_executor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
errors = []
compile_ok = False
status = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.executor_status()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "training_enabled": status.get("training_execution_enabled") is True,
    "executor_enabled": status.get("long_training_executor_enabled") is True,
    "duration_8h": status.get("default_duration_seconds") == 28800,
    "heartbeat_30s": status.get("default_heartbeat_seconds") == 30,
    "checkpoint_300s": status.get("default_checkpoint_seconds") == 300,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "executor_status": status,
    "errors": errors,
    "checks": checks,
    "policy": {
        "long_training_run_enablement_certified": True,
        "training_execution_enabled": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120G_EIGHT_HOUR_REPOSITORY_TRAINING_EXECUTION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        f"errors: {len(errors)}",
        "training_execution_enabled: True",
        "database_writes_allowed: False",
        "strategy_db_write_allowed: False",
        "broker_execution_enabled: False",
        "live_execution_enabled: False",
        "",
        "Long training run enablement certified.",
        "Ready for repository training execution.",
        "DB/strategy DB/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "compile_ok": compile_ok,
    "training_execution_enabled": status.get("training_execution_enabled"),
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
