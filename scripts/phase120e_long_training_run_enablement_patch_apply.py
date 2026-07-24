#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "long_training_run_enablement_patch_preview/120D_long_training_run_enablement_patch_preview_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py"

OUT_DIR = ARCH / "long_training_run_enablement_patch_apply"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120E_long_training_run_enablement_patch_apply_latest.json"
OUT_TXT = OUT_DIR / "120E_long_training_run_enablement_patch_apply_latest.txt"

PHASE = "120E_LONG_TRAINING_RUN_ENABLEMENT_PATCH_APPLY"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

text_before = TARGET.read_text(encoding="utf-8")
text_after = text_before.replace(
    "TRAINING_EXECUTION_ENABLED = False",
    "TRAINING_EXECUTION_ENABLED = True",
    1,
)

TARGET.write_text(text_after, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {"type": type(exc).__name__, "message": str(exc)}

text = TARGET.read_text(encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "training_enabled": "TRAINING_EXECUTION_ENABLED = True" in text,
    "db_write_still_blocked": "DATABASE_WRITES_ALLOWED = False" in text,
    "strategy_db_write_still_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_still_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_still_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in text
        and "LIVE_EXECUTION_ENABLED = False" in text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "compile_error": compile_error,
    "checks": checks,
    "policy": {
        "training_execution_enabled": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120F_LONG_TRAINING_RUN_ENABLEMENT_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "training_execution_enabled: True",
        "database_writes_allowed: False",
        "strategy_db_write_allowed: False",
        "broker_execution_enabled: False",
        "live_execution_enabled: False",
        "",
        "Long training execution enabled.",
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
    "training_execution_enabled": True,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
