#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "temp_fetch_gate_patch_preview" / "77P_temp_fetch_gate_patch_preview_latest.json"
GATE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/real_historical_bar_fetch_gate.py"

OUT_DIR = ARCH / "temp_fetch_gate_patch_apply"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77Q_temp_fetch_gate_patch_apply_latest.json"
OUT_TXT = OUT_DIR / "77Q_temp_fetch_gate_patch_apply_latest.txt"

PHASE = "77Q_TEMP_FETCH_GATE_PATCH_APPLY"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
before = GATE.read_text(encoding="utf-8")

after = before.replace(
    "HISTORICAL_BAR_FETCH_ENABLED = False",
    "HISTORICAL_BAR_FETCH_ENABLED = True",
    1,
)

GATE.write_text(after, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(GATE), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {"type": type(exc).__name__, "message": str(exc)}

text = GATE.read_text(encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "gate_exists": GATE.exists(),
    "gate_compile_ok": compile_ok,
    "fetch_temp_enabled": "HISTORICAL_BAR_FETCH_ENABLED = True" in text,
    "real_replay_still_disabled": "REAL_HISTORICAL_REPLAY_ENABLED = False" in text,
    "training_still_disabled": "TRAINING_ENABLED = False" in text,
    "strategy_db_write_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in text
        and "LIVE_EXECUTION_ENABLED = False" in text
    ),
    "scope_still_limited": (
        "MAX_SYMBOLS_ALLOWED = 1" in text
        and "MAX_ROWS_ALLOWED = 300" in text
        and 'SYMBOL_ALLOWLIST = ["VFV.TO"]' in text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TEMP_FETCH_GATE_PATCH_APPLY",
    "source_preview": str(SOURCE),
    "target_gate": str(GATE),
    "compile_error": compile_error,
    "policy": {
        "historical_bar_fetch_temp_enabled": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "required_relock_phase": "77S_FETCH_GATE_RELOCK",
    },
    "checks": checks,
    "recommended_next_phase": "77R_FETCH_ONE_SYMBOL_READ_ONLY_BARS",
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
        "TEMP FETCH ENABLED ONLY.",
        "Replay/training/db/promotion/broker/live remain blocked.",
        "Relock required after fetch.",
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
    "required_relock_phase": "77S_FETCH_GATE_RELOCK",
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
