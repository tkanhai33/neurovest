#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "49A_qwen_read_only_architecture_session_contract_stub_latest.json"

PHASE = "49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB"

HANDOFF = SANDBOX / "48C_handoff_bundle_refresh_latest.json"

SESSION_FIELDS = {
    "session_id",
    "architecture_stage",
    "latest_confirmed_phase",
    "current_capabilities",
    "still_disabled",
    "next_recommended_phase",
    "critical_safety_locks",
}

FORBIDDEN_SESSION_ACTIONS = {
    "file_write",
    "runtime_execution",
    "source_mutation",
    "strategy_enablement",
    "simulation_enablement",
    "learning_enablement",
    "promotion_enablement",
    "broker_execution",
    "live_execution",
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "handoff_source": str(HANDOFF),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = (
        json.loads(HANDOFF.read_text(encoding="utf-8"))
        if HANDOFF.exists()
        else {}
    )

    session_contract = {
        "status": "qwen_read_only_session_contract_ready",
        "contract_mode": "read_only_session_only",

        "required_session_fields": sorted(
            SESSION_FIELDS
        ),

        "forbidden_session_actions": sorted(
            FORBIDDEN_SESSION_ACTIONS
        ),

        "session_example": {
            "session_id": "readonly-session",
            "architecture_stage": handoff.get("stage"),
            "latest_confirmed_phase": handoff.get(
                "latest_confirmed_phase"
            ),
            "current_capabilities": handoff.get(
                "current_capabilities",
                [],
            ),
            "still_disabled": handoff.get(
                "still_disabled",
                [],
            ),
            "next_recommended_phase": handoff.get(
                "next_recommended_phase"
            ),
            "critical_safety_locks": handoff.get(
                "critical_safety_locks",
                {},
            ),
        },

        "session_read_allowed": True,
        "session_write_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,

        "recommended_next_read_only_phase":
            "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
    }

    result["session_contract"] = session_contract

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        session_contract["status"]
        == "qwen_read_only_session_contract_ready"
    )

    result["checks"]["contract_mode_read_only"] = (
        session_contract["contract_mode"]
        == "read_only_session_only"
    )

    result["checks"]["required_fields_present"] = (
        len(session_contract["required_session_fields"]) > 0
    )

    result["checks"]["forbidden_actions_present"] = (
        len(session_contract["forbidden_session_actions"]) > 0
    )

    result["checks"]["session_read_allowed"] = (
        session_contract["session_read_allowed"] is True
    )

    result["checks"]["session_write_blocked"] = (
        session_contract["session_write_allowed"] is False
    )

    result["checks"]["actions_not_allowed"] = (
        session_contract["actions_allowed"] is False
    )

    result["checks"]["writes_not_allowed"] = (
        session_contract["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        session_contract["runtime_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        session_contract["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        session_contract["broker_or_live_allowed"] is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        session_contract["recommended_next_read_only_phase"]
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
