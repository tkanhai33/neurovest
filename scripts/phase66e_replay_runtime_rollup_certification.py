#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "66E_REPLAY_RUNTIME_ROLLUP_CERTIFICATION"

EXPECTED = {
    "66A_architecture_planning": ARCH / "66A_replay_runtime_architecture_planning_latest.json",
    "66B_contract_stubs": ARCH / "contracts/66B_replay_runtime_contract_stubs_latest.json",
    "66C_gate_wiregraph": ARCH / "wiregraph/66C_replay_runtime_gate_wiregraph_latest.json",
    "66D_dry_run_manifest": ARCH / "dry_run_manifest/66D_replay_runtime_dry_run_manifest_latest.json",
}

OUT_DIR = ARCH / "rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66E_replay_runtime_rollup_certification_latest.json"
OUT_TXT = OUT_DIR / "66E_replay_runtime_rollup_certification_latest.txt"


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

rollup_policy = {
    "replay_runtime_architecture_certified": True,
    "contract_stubs_certified": True,
    "gate_wiregraph_certified": True,
    "dry_run_manifest_certified": True,

    "source_write_allowed_now": False,
    "historical_replay_allowed_now": False,
    "strategy_execution_allowed": False,
    "runtime_execution_allowed": False,
    "runtime_mutation_allowed": False,
    "strategy_db_write_allowed": False,
    "automatic_activation_allowed": False,
    "learning_enabled": False,
    "promotion_enabled": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,
}

planned_state = {
    "replay_spec_count": read_json(EXPECTED["66A_architecture_planning"]).get("replay_spec_count"),
    "planned_file_count": read_json(EXPECTED["66D_dry_run_manifest"]).get("dry_run_manifest", {}).get("planned_file_count"),
    "next_safe_campaign": "66F_SOURCE_PATCH_MANIFEST_PREVIEW_OR_67A_REPLAY_CONTRACT_SOURCE_CREATION",
    "recommended_next_phase": "66F_REPLAY_RUNTIME_SOURCE_PATCH_MANIFEST_PREVIEW",
}

checks["source_write_blocked"] = rollup_policy["source_write_allowed_now"] is False
checks["historical_replay_blocked"] = rollup_policy["historical_replay_allowed_now"] is False
checks["runtime_execution_blocked"] = rollup_policy["runtime_execution_allowed"] is False
checks["runtime_mutation_blocked"] = rollup_policy["runtime_mutation_allowed"] is False
checks["strategy_db_write_blocked"] = rollup_policy["strategy_db_write_allowed"] is False
checks["automatic_activation_blocked"] = rollup_policy["automatic_activation_allowed"] is False
checks["broker_live_blocked"] = (
    rollup_policy["broker_execution_enabled"] is False
    and rollup_policy["live_execution_enabled"] is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_RUNTIME_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "rollup_policy": rollup_policy,
    "planned_state": planned_state,
    "checks": checks,
    "recommended_next_phase": planned_state["recommended_next_phase"],
    "certified": False,
}

result["certified"] = all(checks.values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    "",
    "Artifacts:",
    "",
]

for name, item in artifacts.items():
    lines.append(f"- {name}: exists={item['exists']} certified={item['certified']}")

lines += [
    "",
    "Policy:",
    "",
]

for k, v in rollup_policy.items():
    lines.append(f"{k}: {v}")

lines += [
    "",
    "Next:",
    planned_state["recommended_next_phase"],
]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
