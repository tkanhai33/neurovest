#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
SOURCE = ARCH / "wiregraph" / "66C_replay_runtime_gate_wiregraph_latest.json"

OUT_DIR = ARCH / "dry_run_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66D_replay_runtime_dry_run_manifest_latest.json"
OUT_TXT = OUT_DIR / "66D_replay_runtime_dry_run_manifest_latest.txt"

PHASE = "66D_REPLAY_RUNTIME_DRY_RUN_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

planned_files = [
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L2_domain/replay_spec_contract.py",
        "purpose": "Typed replay spec validation contract",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L2_domain/bar_replay_math_contract.py",
        "purpose": "Pure math contract for bar replay calculations",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L2_domain/replay_metric_contract.py",
        "purpose": "Metric result shape for replay scorecards",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/replay_enablement_gate.py",
        "purpose": "Gate that keeps historical replay disabled until certified",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/replay_plan_service.py",
        "purpose": "Future facade for validating replay specs before execution",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L4_runtime_orchestration/replay_controller.py",
        "purpose": "Future orchestration controller for replay execution",
        "write_allowed_now": False,
    },
    {
        "path": "backend/app/stacks/strategy_candidate_sandbox/L7_tests/test_replay_contracts.py",
        "purpose": "Future contract tests before replay activation",
        "write_allowed_now": False,
    },
]

dry_run_manifest = {
    "planned_file_count": len(planned_files),
    "planned_files": planned_files,
    "activation_order_future": [
        "create_contract_shapes",
        "validate_existing_41_replay_specs",
        "create_fixture_bar_dataset",
        "run contract tests only",
        "certify dry-run replay calculator",
        "enable single fixture replay only",
        "certify no strategy/db/broker writes",
    ],
    "forbidden_now": [
        "write planned source files",
        "execute replay",
        "calculate candidate performance",
        "write strategy database",
        "promote candidates",
        "enable learning",
        "place broker orders",
        "enable live trading",
    ],
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_RUNTIME_DRY_RUN_MANIFEST",
    "source_wiregraph": str(SOURCE),
    "dry_run_manifest": dry_run_manifest,
    "global_policy": {
        "dry_run_manifest_allowed": True,
        "source_write_allowed_now": False,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_exists": SOURCE.exists(),
        "source_certified": source.get("certified") is True,
        "planned_files_present": len(planned_files) > 0,
        "all_planned_writes_blocked": all(f["write_allowed_now"] is False for f in planned_files),
        "source_write_blocked": False is False,
        "replay_blocked": False is False,
        "runtime_execution_blocked": False is False,
        "strategy_db_write_blocked": False is False,
        "promotion_blocked": False is False,
        "broker_live_blocked": False is False,
    },
    "recommended_next_phase": "66E_REPLAY_RUNTIME_ROLLUP_CERTIFICATION",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"planned_file_count: {len(planned_files)}",
    "",
    "Planned files:",
    "",
]

for item in planned_files:
    lines.append(f"- {item['path']} | write_allowed_now={item['write_allowed_now']}")

lines += ["", "Forbidden now:", ""]
for item in dry_run_manifest["forbidden_now"]:
    lines.append(f"- {item}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "planned_file_count": len(planned_files),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))
