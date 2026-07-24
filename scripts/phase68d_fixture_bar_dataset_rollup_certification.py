#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
BASE = ARCH / "fixture_bar_dataset"

PHASE = "68D_FIXTURE_BAR_DATASET_ROLLUP_CERTIFICATION"

EXPECTED = {
    "68A_manifest": BASE / "68A_fixture_bar_dataset_manifest_latest.json",
    "68B_source_creation": BASE / "68B_fixture_bar_dataset_source_creation_latest.json",
    "68C_validation": BASE / "68C_fixture_bar_dataset_validation_latest.json",
}

OUT_JSON = BASE / "68D_fixture_bar_dataset_rollup_certification_latest.json"
OUT_TXT = BASE / "68D_fixture_bar_dataset_rollup_certification_latest.txt"


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

validation = read_json(EXPECTED["68C_validation"])

checks["fixture_rows_validated"] = validation.get("row_count") == 10
checks["historical_replay_blocked"] = validation.get("policy", {}).get("historical_replay_allowed_now") is False
checks["runtime_execution_blocked"] = validation.get("policy", {}).get("runtime_execution_allowed") is False
checks["strategy_db_write_blocked"] = validation.get("policy", {}).get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = validation.get("policy", {}).get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    validation.get("policy", {}).get("broker_execution_enabled") is False
    and validation.get("policy", {}).get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_BAR_DATASET_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "fixture_summary": {
        "dataset_id": "fixture_ohlcv_v1",
        "row_count": validation.get("row_count"),
        "validated": validation.get("certified") is True,
    },
    "policy": {
        "fixture_dataset_certified": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "68E_FIXTURE_BAR_MATH_CONTRACT_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"dataset_id: fixture_ohlcv_v1",
        f"row_count: {validation.get('row_count')}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "row_count": validation.get("row_count"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
