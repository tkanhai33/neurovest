#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "67F_REPLAY_SPEC_VALIDATION_ROLLUP_CERTIFICATION"

SOURCE = ARCH / "replay_spec_contract_validation" / "67E_replay_spec_contract_validator_latest.json"

OUT_DIR = ARCH / "replay_spec_validation_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "67F_replay_spec_validation_rollup_latest.json"
OUT_TXT = OUT_DIR / "67F_replay_spec_validation_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
validations = source.get("validations", [])

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "specs_present": len(validations) > 0,
    "all_specs_valid": all(v.get("valid") is True for v in validations),
    "no_invalid_specs": source.get("invalid_count") == 0,
    "valid_count_matches_spec_count": source.get("valid_count") == source.get("spec_count"),
    "all_draft_only": all(v.get("checks", {}).get("draft_only_mode") is True for v in validations),
    "all_safety_false": all(v.get("checks", {}).get("all_safety_false") is True for v in validations),
}

policy = {
    "replay_spec_validation_certified": True,
    "historical_replay_allowed_now": False,
    "runtime_execution_allowed": False,
    "runtime_mutation_allowed": False,
    "strategy_execution_allowed": False,
    "strategy_db_write_allowed": False,
    "promotion_enabled": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,
}

checks["historical_replay_blocked"] = policy["historical_replay_allowed_now"] is False
checks["runtime_execution_blocked"] = policy["runtime_execution_allowed"] is False
checks["strategy_db_write_blocked"] = policy["strategy_db_write_allowed"] is False
checks["promotion_blocked"] = policy["promotion_enabled"] is False
checks["broker_live_blocked"] = (
    policy["broker_execution_enabled"] is False
    and policy["live_execution_enabled"] is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_SPEC_VALIDATION_ROLLUP_CERTIFICATION",
    "source_validation": str(SOURCE),
    "spec_count": source.get("spec_count"),
    "valid_count": source.get("valid_count"),
    "invalid_count": source.get("invalid_count"),
    "policy": policy,
    "checks": checks,
    "recommended_next_phase": "68A_FIXTURE_BAR_DATASET_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"spec_count: {result['spec_count']}",
    f"valid_count: {result['valid_count']}",
    f"invalid_count: {result['invalid_count']}",
    "",
    "Policy:",
    "",
]

for k, v in policy.items():
    lines.append(f"{k}: {v}")

lines += ["", "Next:", result["recommended_next_phase"]]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "spec_count": result["spec_count"],
    "valid_count": result["valid_count"],
    "invalid_count": result["invalid_count"],
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
