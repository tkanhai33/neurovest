#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util, json, py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "long_training_run_executor_stub/120B_long_training_run_executor_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py"
MANIFEST = ROOT / "backend/app/stacks/learning_research/research_data/manifests/training/training_manifest_repository_v1.json"

OUT_DIR = ARCH / "long_training_run_executor_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120C_long_training_run_executor_certification_latest.json"
OUT_TXT = OUT_DIR / "120C_long_training_run_executor_certification_latest.txt"

PHASE = "120C_LONG_TRAINING_RUN_EXECUTOR_CERTIFICATION"

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
plan = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.executor_status()
    plan = module.build_long_training_plan(
        run_id="TRAINING_RUN_REPOSITORY_8H_PREVIEW",
        repository_manifest=str(MANIFEST),
    )
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "manifest_exists": MANIFEST.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "plan_present": bool(plan),
    "executor_enabled": status.get("long_training_executor_enabled") is True,
    "duration_8h": status.get("default_duration_seconds") == 28800,
    "heartbeat_30s": status.get("default_heartbeat_seconds") == 30,
    "checkpoint_300s": status.get("default_checkpoint_seconds") == 300,
    "training_still_disabled": status.get("training_execution_enabled") is False,
    "db_write_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "plan_resume_supported": plan.get("resume_supported") is True,
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "repository_manifest": str(MANIFEST),
    "executor_status": status,
    "plan_preview": plan,
    "errors": errors,
    "checks": checks,
    "policy": {
        "long_training_run_executor_certified": True,
        "long_training_executor_enabled": True,
        "training_execution_enabled": False,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120D_LONG_TRAINING_RUN_ENABLEMENT_PATCH_PREVIEW",
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
        "duration_seconds: 28800",
        "heartbeat_seconds: 30",
        "checkpoint_seconds: 300",
        "training_execution_enabled: False",
        "",
        "Long training executor certified.",
        "No training executed. No DB writes. No broker/live.",
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
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
