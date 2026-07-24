#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
BASE = ARCH / "fixture_bar_math_contract"

PHASE = "68G_FIXTURE_BAR_MATH_ROLLUP_CERTIFICATION"

EXPECTED = {
    "68E_math_contract_stub": BASE / "68E_fixture_bar_math_contract_stub_latest.json",
    "68F_math_contract_certification": BASE / "68F_fixture_bar_math_contract_certification_latest.json",
}

OUT_JSON = BASE / "68G_fixture_bar_math_rollup_certification_latest.json"
OUT_TXT = BASE / "68G_fixture_bar_math_rollup_certification_latest.txt"


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

cert = read_json(EXPECTED["68F_math_contract_certification"])

checks["contract_id_present"] = bool(cert.get("contract_id"))
checks["math_execution_blocked"] = cert.get("policy", {}).get("math_execution_allowed_now") is False
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
    "mode": "FIXTURE_BAR_MATH_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "contract_id": cert.get("contract_id"),
    "policy": {
        "fixture_bar_math_contract_rollup_certified": True,
        "math_execution_allowed_now": False,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "69A_FIXTURE_BAR_MATH_FUNCTION_STUB_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"contract_id: {result['contract_id']}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "contract_id": result["contract_id"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
