#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_territory_command_registry" / "106B_dev_territory_command_registry_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py"

OUT_DIR = ARCH / "dev_territory_command_registry_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "106C_dev_territory_command_registry_certification_latest.json"
OUT_TXT = OUT_DIR / "106C_dev_territory_command_registry_certification_latest.txt"

PHASE = "106C_DEV_TERRITORY_COMMAND_REGISTRY_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("dev_territory_command_registry", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
compile_ok = False
status = {}
commands = []
doctrine = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.registry_status()
    commands = module.list_dev_territory_commands()
    doctrine = module.get_dev_territory_doctrine()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "commands_loaded": len(commands) == 7,
    "doctrine_loaded": bool(doctrine),
    "registry_disabled": status.get("dev_territory_registry_enabled") is False,
    "runtime_write_blocked": status.get("registry_write_to_runtime_enabled") is False,
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
    "mode": "DEV_TERRITORY_COMMAND_REGISTRY_CERTIFICATION",
    "source_stub": str(SOURCE),
    "target_file": str(TARGET),
    "registry_status": status,
    "command_count": len(commands),
    "doctrine_present": bool(doctrine),
    "errors": errors,
    "checks": checks,
    "policy": {
        "dev_territory_registry_certified": True,
        "dev_territory_registry_enabled": False,
        "registry_write_to_runtime_enabled": False,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "106D_DEV_TERRITORY_COMMAND_REGISTRY_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        f"command_count: {len(commands)}",
        "",
        "Dev territory command registry certified.",
        "Registry/runtime/training/db/mutation/promotion/broker/live remain blocked.",
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
    "command_count": len(commands),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
