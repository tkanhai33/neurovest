#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_gate_stub" / "75A_training_gate_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/training_enablement_gate.py"

OUT_DIR = ARCH / "training_gate_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "75B_training_gate_certification_latest.json"
OUT_TXT = OUT_DIR / "75B_training_gate_certification_latest.txt"

PHASE = "75B_TRAINING_GATE_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("training_enablement_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
status = {}

compile_ok = False
try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.training_gate_status()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "training_disabled": status.get("training_enabled") is False,
    "self_mutation_blocked": status.get("self_mutation_allowed") is False,
    "autonomous_promotion_blocked": status.get("autonomous_promotion_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_GATE_CERTIFICATION",
    "source_training_gate_stub": str(SOURCE),
    "target_file": str(TARGET),
    "training_gate_status": status,
    "errors": errors,
    "checks": checks,
    "policy": {
        "training_gate_certified": True,
        "training_enabled": False,
        "self_mutation_allowed": False,
        "autonomous_promotion_allowed": False,
        "strategy_db_write_allowed": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "75C_TRAINING_GATE_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "",
        "Training gate status:",
        *[f"- {k}: {v}" for k, v in status.items()],
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
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
