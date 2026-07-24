#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_replay_dry_run_gate" / "77B_real_historical_replay_dry_run_gate_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/real_historical_replay_dry_run_gate.py"

OUT_DIR = ARCH / "real_historical_replay_dry_run_gate_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77C_real_historical_replay_dry_run_gate_certification_latest.json"
OUT_TXT = OUT_DIR / "77C_real_historical_replay_dry_run_gate_certification_latest.txt"

PHASE = "77C_REAL_HISTORICAL_REPLAY_DRY_RUN_GATE_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("real_historical_replay_dry_run_gate", path)
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
    status = module.real_historical_replay_gate_status()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "real_historical_replay_disabled": status.get("real_historical_replay_enabled") is False,
    "training_disabled": status.get("training_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "scope_limited": (
        status.get("max_specs_allowed") == 1
        and status.get("max_symbols_allowed") == 1
        and status.get("max_rows_allowed") == 300
    ),
    "allowlist_limited": status.get("initial_symbol_allowlist") == ["VFV.TO"],
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_REPLAY_DRY_RUN_GATE_CERTIFICATION",
    "source_gate_stub": str(SOURCE),
    "target_file": str(TARGET),
    "gate_status": status,
    "errors": errors,
    "checks": checks,
    "policy": {
        "real_historical_replay_gate_certified": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "77D_REAL_HISTORICAL_REPLAY_GATE_ROLLUP",
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
        "Gate status:",
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
