#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

ROLLUP = ARCH / "contract_import_rollup" / "67D_replay_contract_import_rollup_latest.json"
SPECS = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies" / "replay_specs" / "65G_replay_spec_draft_builder_latest.json"

OUT_DIR = ARCH / "replay_spec_contract_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "67E_replay_spec_contract_validator_latest.json"
OUT_TXT = OUT_DIR / "67E_replay_spec_contract_validator_latest.txt"

PHASE = "67E_REPLAY_SPEC_CONTRACT_VALIDATOR"

REQUIRED_FIELDS = [
    "spec_id",
    "candidate_id",
    "strategy_name",
    "asset_class",
    "signal_family",
    "replay_scope",
    "formula_requirements",
    "metrics_required",
    "stress_tests_required",
    "safety",
]

REQUIRED_SCOPE_FIELDS = [
    "mode",
    "historical_replay_allowed_now",
    "default_period",
    "default_interval",
    "minimum_candles",
    "symbols",
    "data_sources",
]

REQUIRED_SAFETY_FALSE_FIELDS = [
    "historical_replay_allowed_now",
    "strategy_execution_allowed",
    "implementation_patch_allowed",
    "runtime_execution_allowed",
    "runtime_mutation_allowed",
    "learning_enabled",
    "promotion_enabled",
    "broker_execution_enabled",
    "live_execution_enabled",
]


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


rollup = read_json(ROLLUP)
spec_bundle = read_json(SPECS)
specs = []

for file_name in spec_bundle.get("spec_files", []):
    spec_path = SPECS.parent / file_name
    spec_data = read_json(spec_path)
    specs.append({
        "file": str(spec_path),
        "data": spec_data,
    })

validations = []

for item in specs:
    spec = item["data"]
    replay_scope = spec.get("replay_scope", {}) if isinstance(spec.get("replay_scope"), dict) else {}
    safety = spec.get("safety", {}) if isinstance(spec.get("safety"), dict) else {}

    missing_fields = [field for field in REQUIRED_FIELDS if field not in spec]
    missing_scope_fields = [field for field in REQUIRED_SCOPE_FIELDS if field not in replay_scope]

    safety_false_ok = all(
        safety.get(field) is False
        for field in REQUIRED_SAFETY_FALSE_FIELDS
    )

    checks = {
        "file_loaded": bool(spec),
        "required_fields_present": len(missing_fields) == 0,
        "required_scope_fields_present": len(missing_scope_fields) == 0,
        "draft_only_mode": replay_scope.get("mode") == "DRAFT_ONLY",
        "symbols_present": isinstance(replay_scope.get("symbols"), list) and len(replay_scope.get("symbols", [])) > 0,
        "data_sources_present": isinstance(replay_scope.get("data_sources"), list) and len(replay_scope.get("data_sources", [])) > 0,
        "metrics_present": isinstance(spec.get("metrics_required"), list) and len(spec.get("metrics_required", [])) > 0,
        "stress_tests_present": isinstance(spec.get("stress_tests_required"), list) and len(spec.get("stress_tests_required", [])) > 0,
        "all_safety_false": safety_false_ok,
    }

    validations.append({
        "file": item["file"],
        "spec_id": spec.get("spec_id"),
        "candidate_id": spec.get("candidate_id"),
        "strategy_name": spec.get("strategy_name"),
        "missing_fields": missing_fields,
        "missing_scope_fields": missing_scope_fields,
        "checks": checks,
        "valid": all(checks.values()),
    })

checks = {
    "rollup_exists": ROLLUP.exists(),
    "rollup_certified": rollup.get("certified") is True,
    "spec_bundle_exists": SPECS.exists(),
    "spec_bundle_certified": spec_bundle.get("certified") is True,
    "specs_present": len(specs) > 0,
    "all_specs_valid": all(v["valid"] for v in validations),
    "all_specs_draft_only": all(v["checks"]["draft_only_mode"] for v in validations),
    "all_safety_false": all(v["checks"]["all_safety_false"] for v in validations),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_SPEC_CONTRACT_VALIDATOR",
    "source_rollup": str(ROLLUP),
    "source_replay_specs": str(SPECS),
    "spec_count": len(specs),
    "valid_count": sum(1 for v in validations if v["valid"]),
    "invalid_count": sum(1 for v in validations if not v["valid"]),
    "validations": validations,
    "policy": {
        "spec_validation_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "67F_REPLAY_SPEC_VALIDATION_ROLLUP_CERTIFICATION",
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
    "Validated specs:",
    "",
]

for v in validations:
    lines.append(f"- {v['spec_id']} | valid={v['valid']} | {v['strategy_name']}")

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
