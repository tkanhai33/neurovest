#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
LIB = ROOT / "runtime" / "research_library"

SOURCE = LIB / "pipeline_rollup" / "65M_research_pipeline_rollup_latest.json"
SPECS = LIB / "strategy_sources" / "151_trading_strategies" / "replay_specs" / "65G_replay_spec_draft_builder_latest.json"

OUT_DIR = ROOT / "runtime" / "replay_runtime_architecture"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66A_replay_runtime_architecture_planning_latest.json"
OUT_TXT = OUT_DIR / "66A_replay_runtime_architecture_planning_latest.txt"

PHASE = "66A_REPLAY_RUNTIME_ARCHITECTURE_PLANNING"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


rollup = read_json(SOURCE)
specs = read_json(SPECS)
spec_count = specs.get("replay_spec_count", 0)

architecture_plan = {
    "runtime_goal": "consume certified replay spec drafts and prepare replay architecture only",
    "input_artifacts": [
        str(SOURCE),
        str(SPECS),
    ],
    "planned_layers": {
        "L0_external_adapter": [
            "yfinance_historical_bars",
            "FRED_API_READ_ONLY",
            "STATCAN_READ_ONLY",
            "future_options_chain_provider",
            "future_volatility_provider",
        ],
        "L1_security_auth_safety": [
            "replay_enablement_gate",
            "runtime_execution_gate",
            "promotion_gate",
            "broker_live_gate",
        ],
        "L2_domain": [
            "replay_spec_contract",
            "bar_replay_math_contract",
            "metric_contract",
            "stress_test_contract",
            "decision_policy_contract",
        ],
        "L3_service_facade": [
            "replay_plan_service",
            "historical_bar_source_service",
            "metric_scorecard_service",
        ],
        "L4_runtime_orchestration": [
            "replay_controller_planned",
            "stress_test_controller_planned",
            "candidate_result_router_planned",
        ],
        "L5_api_presentation": [
            "read_only_replay_status_endpoint_future",
            "read_only_candidate_report_endpoint_future",
        ],
        "L6_frontend": [
            "read_only_replay_dashboard_future",
            "candidate_review_panel_future",
        ],
        "L7_tests": [
            "replay_contract_tests",
            "safety_gate_tests",
            "fixture_bar_replay_tests",
        ],
    },
    "runtime_flow_planned": [
        "replay_spec_draft",
        "replay_enablement_gate",
        "historical_data_adapter",
        "bar_replay_engine",
        "metric_scorecard",
        "stress_test_report",
        "decision_gate_preview",
        "inactive_strategy_databank_candidate_only",
    ],
    "decision_policy": {
        "pass_destination": "INACTIVE_STRATEGY_DATABANK_CANDIDATE",
        "near_miss_band_percent": {"min": 2, "max": 10},
        "near_miss_action": "CONTROLLED_REFACTOR_QUEUE",
        "max_refactor_attempts": 3,
        "fail_after_max_attempts": "QUARANTINE_OR_TRASH",
        "activation_requires_manual_gate": True,
    },
    "safety_policy": {
        "architecture_planning_allowed": True,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_RUNTIME_ARCHITECTURE_PLANNING",
    "source_rollup": str(SOURCE),
    "source_replay_specs": str(SPECS),
    "replay_spec_count": spec_count,
    "architecture_plan": architecture_plan,
    "checks": {
        "source_rollup_exists": SOURCE.exists(),
        "source_rollup_certified": rollup.get("certified") is True,
        "source_specs_exists": SPECS.exists(),
        "source_specs_certified": specs.get("certified") is True,
        "replay_specs_present": spec_count > 0,
        "architecture_plan_present": bool(architecture_plan),
        "historical_replay_still_blocked": architecture_plan["safety_policy"]["historical_replay_allowed_now"] is False,
        "runtime_execution_blocked": architecture_plan["safety_policy"]["runtime_execution_allowed"] is False,
        "runtime_mutation_blocked": architecture_plan["safety_policy"]["runtime_mutation_allowed"] is False,
        "promotion_blocked": architecture_plan["safety_policy"]["promotion_enabled"] is False,
        "broker_live_blocked": (
            architecture_plan["safety_policy"]["broker_execution_enabled"] is False
            and architecture_plan["safety_policy"]["live_execution_enabled"] is False
        ),
    },
    "recommended_next_phase": "66B_REPLAY_RUNTIME_CONTRACT_STUBS",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"replay_spec_count: {spec_count}",
    "",
    "Planned Replay Flow:",
    "",
]

for step in architecture_plan["runtime_flow_planned"]:
    lines.append(f"- {step}")

lines += [
    "",
    "Safety:",
    "",
]

for k, v in architecture_plan["safety_policy"].items():
    lines.append(f"{k}: {v}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "replay_spec_count": spec_count,
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))
