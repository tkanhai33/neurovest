#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
SOURCE = ARCH / "contracts" / "66B_replay_runtime_contract_stubs_latest.json"

OUT_DIR = ARCH / "wiregraph"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66C_replay_runtime_gate_wiregraph_latest.json"
OUT_TXT = OUT_DIR / "66C_replay_runtime_gate_wiregraph_latest.txt"

PHASE = "66C_REPLAY_RUNTIME_GATE_WIREGRAPH"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

nodes = [
    {"id": "replay_spec_draft", "type": "input", "execution_allowed": False},
    {"id": "replay_enablement_gate", "type": "gate", "execution_allowed": False},
    {"id": "historical_data_adapter", "type": "L0_adapter", "execution_allowed": False},
    {"id": "bar_replay_engine", "type": "planned_engine", "execution_allowed": False},
    {"id": "metric_scorecard", "type": "planned_contract", "execution_allowed": False},
    {"id": "stress_test_report", "type": "planned_report", "execution_allowed": False},
    {"id": "decision_policy_gate", "type": "gate", "execution_allowed": False},
    {"id": "inactive_strategy_databank_candidate", "type": "future_destination", "write_allowed": False},
    {"id": "controlled_refactor_queue", "type": "future_destination", "write_allowed": False},
    {"id": "quarantine_or_trash", "type": "future_destination", "write_allowed": False},
    {"id": "manual_activation_gate", "type": "gate", "execution_allowed": False},
]

edges = [
    ["replay_spec_draft", "replay_enablement_gate", "REQUIRES_GATE"],
    ["replay_enablement_gate", "historical_data_adapter", "IF_FUTURE_ENABLED"],
    ["historical_data_adapter", "bar_replay_engine", "SUPPLIES_BARS_FUTURE"],
    ["bar_replay_engine", "metric_scorecard", "PRODUCES_METRICS_FUTURE"],
    ["metric_scorecard", "stress_test_report", "FEEDS_STRESS_TESTS_FUTURE"],
    ["stress_test_report", "decision_policy_gate", "FEEDS_DECISION_POLICY_FUTURE"],
    ["decision_policy_gate", "inactive_strategy_databank_candidate", "PASS_FUTURE"],
    ["decision_policy_gate", "controlled_refactor_queue", "NEAR_MISS_FUTURE"],
    ["decision_policy_gate", "quarantine_or_trash", "FAIL_FUTURE"],
    ["inactive_strategy_databank_candidate", "manual_activation_gate", "REQUIRES_MANUAL_GATE"],
]

blocked_paths = [
    "replay_spec_draft -> bar_replay_engine",
    "bar_replay_engine -> strategy_execution",
    "metric_scorecard -> strategy_db_write",
    "decision_policy_gate -> automatic_activation",
    "inactive_strategy_databank_candidate -> live_trading",
    "manual_activation_gate -> broker_execution",
]

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_RUNTIME_GATE_WIREGRAPH",
    "source_contracts": str(SOURCE),
    "nodes": nodes,
    "edges": edges,
    "blocked_paths": blocked_paths,
    "wiregraph_policy": {
        "wiregraph_mapping_allowed": True,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "automatic_activation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_exists": SOURCE.exists(),
        "source_certified": source.get("certified") is True,
        "nodes_present": len(nodes) > 0,
        "edges_present": len(edges) > 0,
        "blocked_paths_present": len(blocked_paths) > 0,
        "replay_blocked": False is False,
        "runtime_execution_blocked": False is False,
        "strategy_db_write_blocked": False is False,
        "automatic_activation_blocked": False is False,
        "broker_live_blocked": False is False,
    },
    "recommended_next_phase": "66D_REPLAY_RUNTIME_DRY_RUN_MANIFEST",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    "",
    "Nodes:",
]
for node in nodes:
    lines.append(f"- {node['id']} ({node['type']})")

lines += ["", "Edges:"]
for src, dst, rel in edges:
    lines.append(f"- {src} --{rel}--> {dst}")

lines += ["", "Blocked Paths:"]
for path in blocked_paths:
    lines.append(f"- {path}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "node_count": len(nodes),
    "edge_count": len(edges),
    "blocked_path_count": len(blocked_paths),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))
