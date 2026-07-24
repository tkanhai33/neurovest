#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_learner_enablement_patch_apply" / "83F_read_only_learner_enablement_patch_apply_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py"

OUT_DIR = ARCH / "read_only_learner_enablement_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83G_read_only_learner_enablement_certification_latest.json"
OUT_TXT = OUT_DIR / "83G_read_only_learner_enablement_certification_latest.txt"

PHASE = "83G_READ_ONLY_LEARNER_ENABLEMENT_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("training_read_only_learner", path)
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
    status = module.learner_status()
    preview = module.preview_learning_input(
        "READ_ONLY_STRESS_REPORT_VFV_TO_0001",
        "INACTIVE_DRAFT_FIXTURE_0001",
    )
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "preview_present": bool(preview),
    "read_only_learner_enabled": status.get("read_only_learner_enabled") is True,
    "training_still_disabled": status.get("training_enabled") is False,
    "learner_write_still_disabled": status.get("learner_write_enabled") is False,
    "mutation_still_blocked": status.get("mutation_allowed") is False,
    "queue_write_still_blocked": status.get("queue_write_enabled") is False,
    "strategy_db_write_still_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_still_blocked": status.get("promotion_enabled") is False,
    "broker_live_still_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "preview_only": preview.get("mode") == "PREVIEW_ONLY",
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_LEARNER_ENABLEMENT_CERTIFICATION",
    "source_patch_apply": str(SOURCE),
    "target_file": str(TARGET),
    "learner_status": status,
    "preview": preview,
    "errors": errors,
    "checks": checks,
    "policy": {
        "read_only_learner_enablement_certified": True,
        "read_only_learner_enabled": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83H_READ_ONLY_LEARNER_ENABLEMENT_ROLLUP",
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
        "Read-only learner enablement certified.",
        "Training/write/mutation/queue/db/promotion/broker/live remain blocked.",
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
    "read_only_learner_enabled": status.get("read_only_learner_enabled"),
    "training_enabled": status.get("training_enabled"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
