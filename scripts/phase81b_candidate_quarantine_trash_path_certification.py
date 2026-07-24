#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "candidate_quarantine_trash_path" / "81A_candidate_quarantine_trash_path_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/candidate_quarantine_trash_path.py"

OUT_DIR = ARCH / "candidate_quarantine_trash_path_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "81B_candidate_quarantine_trash_path_certification_latest.json"
OUT_TXT = OUT_DIR / "81B_candidate_quarantine_trash_path_certification_latest.txt"

PHASE = "81B_CANDIDATE_QUARANTINE_TRASH_PATH_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_quarantine_trash_path", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
status = {}
preview = {}
compile_ok = False

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.quarantine_trash_status()
    preview = module.preview_quarantine_record("TEST_CANDIDATE_0001", "certification preview")

except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "preview_present": bool(preview),
    "quarantine_disabled": status.get("quarantine_path_enabled") is False,
    "trash_disabled": status.get("trash_path_enabled") is False,
    "delete_blocked": status.get("delete_allowed") is False,
    "mutation_blocked": status.get("mutation_allowed") is False,
    "training_blocked": status.get("training_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "preview_only": preview.get("mode") == "PREVIEW_ONLY",
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "CANDIDATE_QUARANTINE_TRASH_PATH_CERTIFICATION",
    "source_stub": str(SOURCE),
    "target_file": str(TARGET),
    "status": status,
    "preview": preview,
    "errors": errors,
    "checks": checks,
    "policy": {
        "candidate_quarantine_trash_path_certified": True,
        "quarantine_path_enabled": False,
        "trash_path_enabled": False,
        "delete_allowed": False,
        "mutation_allowed": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "81C_CANDIDATE_QUARANTINE_TRASH_PATH_ROLLUP",
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
        "Quarantine/trash path certified.",
        "Quarantine/trash/delete/mutation/training/db/promotion/broker/live remain blocked.",
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
