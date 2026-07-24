#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "70D_FIXTURE_REPLAY_CALCULATOR_ROLLUP"

EXPECTED = {
    "70A_preview": ARCH / "fixture_replay_calculator_preview/70A_fixture_replay_calculator_dry_run_preview_latest.json",
    "70B_source_creation": ARCH / "fixture_replay_calculator_source/70B_fixture_replay_calculator_source_creation_latest.json",
    "70C_certification": ARCH / "fixture_replay_calculator_certification/70C_fixture_replay_calculator_certification_latest.json",
}

OUT_DIR = ARCH / "fixture_replay_calculator_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "70D_fixture_replay_calculator_rollup_latest.json"
OUT_TXT = OUT_DIR / "70D_fixture_replay_calculator_rollup_latest.txt"


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

cert = read_json(EXPECTED["70C_certification"])
tests = cert.get("tests", {})

checks["tests_present"] = len(tests) > 0
checks["all_tests_passed"] = all(tests.values()) if tests else False
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
    "mode": "FIXTURE_REPLAY_CALCULATOR_ROLLUP",
    "artifacts": artifacts,
    "test_count": len(tests),
    "policy": {
        "fixture_calculator_rollup_certified": True,
        "fixture_metric_calculation_certified": True,
        "historical_replay_allowed_now": False,
        "strategy_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "71A_SINGLE_FIXTURE_REPLAY_DRY_RUN_ONLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"test_count: {len(tests)}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "test_count": len(tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
