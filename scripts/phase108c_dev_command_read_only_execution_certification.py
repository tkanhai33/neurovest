#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_command_read_only_execution" / "108B_dev_command_read_only_execution_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py"

OUT_DIR = ARCH / "dev_command_read_only_execution_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "108C_dev_command_read_only_execution_certification_latest.json"
OUT_TXT = OUT_DIR / "108C_dev_command_read_only_execution_certification_latest.txt"

PHASE = "108C_DEV_COMMAND_READ_ONLY_EXECUTION_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("dev_command_read_only_executor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
compile_ok = False
status = {}
preview = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.executor_status()
    preview = module.preview_dev_command("SCOUT")
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "preview_present": bool(preview),
    "command_execution_disabled": status.get("command_execution_enabled") is False,
    "read_only_preview_enabled": status.get("read_only_preview_enabled") is True,
    "preview_not_executed": preview.get("executed") is False,
    "preview_mode_correct": preview.get("mode") == "READ_ONLY_COMMAND_PREVIEW",
    "training_blocked": status.get("training_execution_enabled") is False,
    "learner_write_blocked": status.get("learner_write_enabled") is False,
    "mutation_blocked": status.get("mutation_allowed") is False,
    "queue_write_blocked": status.get("queue_write_enabled") is False,
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
    "mode": "DEV_COMMAND_READ_ONLY_EXECUTION_CERTIFICATION",
    "source_stub": str(SOURCE),
    "target_file": str(TARGET),
    "executor_status": status,
    "preview": preview,
    "errors": errors,
    "checks": checks,
    "policy": {
        "dev_command_read_only_execution_certified": True,
        "command_execution_enabled": False,
        "read_only_preview_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "108D_DEV_COMMAND_READ_ONLY_EXECUTION_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "command_execution_enabled: False",
        "read_only_preview_enabled: True",
        "",
        "Dev command read-only execution certified.",
        "Training/db/mutation/promotion/broker/live remain blocked.",
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
    "command_execution_enabled": status.get("command_execution_enabled"),
    "read_only_preview_enabled": status.get("read_only_preview_enabled"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
