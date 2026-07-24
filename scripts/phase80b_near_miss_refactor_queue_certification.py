#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "near_miss_refactor_queue" / "80A_near_miss_refactor_queue_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/near_miss_refactor_queue.py"

OUT_DIR = ARCH / "near_miss_refactor_queue_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "80B_near_miss_refactor_queue_certification_latest.json"
OUT_TXT = OUT_DIR / "80B_near_miss_refactor_queue_certification_latest.txt"

PHASE = "80B_NEAR_MISS_REFACTOR_QUEUE_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("near_miss_refactor_queue", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
status = {}
tests = {}
compile_ok = False

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.near_miss_queue_status()

    tests["status_present"] = bool(status)
    tests["attempts_capped_at_3"] = status.get("max_refactor_attempts") == 3
    tests["queue_write_disabled"] = status.get("queue_write_enabled") is False
    tests["mutation_blocked"] = status.get("mutation_allowed") is False
    tests["training_blocked"] = status.get("training_enabled") is False
    tests["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
    tests["promotion_blocked"] = status.get("promotion_enabled") is False
    tests["broker_live_blocked"] = (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    )

    tests["attempt_0_allowed"] = module.validate_attempt_count(0).get("allowed") is True
    tests["attempt_3_allowed"] = module.validate_attempt_count(3).get("allowed") is True
    tests["attempt_4_blocked"] = module.validate_attempt_count(4).get("allowed") is False
    tests["negative_attempt_blocked"] = module.validate_attempt_count(-1).get("allowed") is False

except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "tests_present": len(tests) > 0,
    "all_tests_passed": all(tests.values()) if tests else False,
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NEAR_MISS_REFACTOR_QUEUE_CERTIFICATION",
    "source_queue_stub": str(SOURCE),
    "target_file": str(TARGET),
    "queue_status": status,
    "tests": tests,
    "errors": errors,
    "checks": checks,
    "policy": {
        "near_miss_refactor_queue_certified": True,
        "max_refactor_attempts": 3,
        "queue_write_enabled": False,
        "mutation_allowed": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "80C_NEAR_MISS_REFACTOR_QUEUE_ROLLUP",
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
        "Tests:",
        *[f"- {k}: {v}" for k, v in tests.items()],
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
    "test_count": len(tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
