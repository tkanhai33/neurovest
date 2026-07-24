#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "69D_FIXTURE_BAR_MATH_FUNCTION_ROLLUP_CERTIFICATION"

EXPECTED = {
    "69A_function_preview": ARCH / "fixture_bar_math_function_preview/69A_fixture_bar_math_function_stub_preview_latest.json",
    "69B_function_source": ARCH / "fixture_bar_math_function_source/69B_fixture_bar_math_function_source_creation_latest.json",
    "69C_function_certification": ARCH / "fixture_bar_math_function_certification/69C_fixture_bar_math_function_certification_latest.json",
}

OUT_DIR = ARCH / "fixture_bar_math_function_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "69D_fixture_bar_math_function_rollup_latest.json"
OUT_TXT = OUT_DIR / "69D_fixture_bar_math_function_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read_json(path)
    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "phase": data.get("phase"),
        "certified": data.get("certified") is True,
    }
    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = data.get("certified") is True

cert = read_json(EXPECTED["69C_function_certification"])
function_tests = cert.get("function_tests", {})

checks["function_tests_present"] = len(function_tests) > 0
checks["all_function_tests_passed"] = all(function_tests.values()) if function_tests else False
checks["historical_replay_blocked"] = cert.get("policy", {}).get("historical_replay_allowed_now") is False
checks["runtime_execution_blocked"] = cert.get("policy", {}).get("runtime_execution_allowed") is False
checks["strategy_db_write_blocked"] = cert.get("policy", {}).get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = cert.get("policy", {}).get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    cert.get("policy", {}).get("broker_execution_enabled") is False
    and cert.get("policy", {}).get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_BAR_MATH_FUNCTION_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "function_test_count": len(function_tests),
    "function_tests": function_tests,
    "policy": {
        "fixture_bar_math_functions_certified": True,
        "math_helpers_exist": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "70A_FIXTURE_REPLAY_CALCULATOR_DRY_RUN_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"function_test_count: {len(function_tests)}",
        "",
        "Function tests:",
        *[f"- {k}: {v}" for k, v in function_tests.items()],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "function_test_count": len(function_tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
