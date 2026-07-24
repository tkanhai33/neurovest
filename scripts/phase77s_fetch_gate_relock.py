#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fixture" / "77R_fetch_one_symbol_read_only_bars_latest.json"
GATE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/real_historical_bar_fetch_gate.py"

OUT_DIR = ARCH / "fetch_gate_relock"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77S_fetch_gate_relock_latest.json"
OUT_TXT = OUT_DIR / "77S_fetch_gate_relock_latest.txt"

PHASE = "77S_FETCH_GATE_RELOCK"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("real_historical_bar_fetch_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)

text = GATE.read_text(encoding="utf-8")
text = text.replace("HISTORICAL_BAR_FETCH_ENABLED = True", "HISTORICAL_BAR_FETCH_ENABLED = False")
GATE.write_text(text, encoding="utf-8")

errors = []
status = {}
compile_ok = False

try:
    py_compile.compile(str(GATE), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(GATE)
    status = module.historical_bar_fetch_gate_status()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "gate_exists": GATE.exists(),
    "gate_compile_ok": compile_ok,
    "status_present": bool(status),
    "historical_bar_fetch_disabled": status.get("historical_bar_fetch_enabled") is False,
    "real_historical_replay_disabled": status.get("real_historical_replay_enabled") is False,
    "training_disabled": status.get("training_enabled") is False,
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
    "mode": "FETCH_GATE_RELOCK",
    "source_fetch_result": str(SOURCE),
    "gate_file": str(GATE),
    "gate_status": status,
    "errors": errors,
    "checks": checks,
    "policy": {
        "fetch_gate_relocked": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "77T_FETCH_ARTIFACT_CERTIFICATION",
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
        "Gate relocked:",
        f"historical_bar_fetch_enabled: {status.get('historical_bar_fetch_enabled')}",
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
    "historical_bar_fetch_enabled": status.get("historical_bar_fetch_enabled"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
