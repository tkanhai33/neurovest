from __future__ import annotations

from fastapi import APIRouter

from app.stacks.safety_governance.services.safety_governance_service import (
    deny_all_execution_in_skeleton,
    get_safety_governance_state,
)

router = APIRouter(prefix="/safety-governance", tags=["safety-governance"])


@router.get("/status")
def safety_governance_status() -> dict[str, object]:
    state = get_safety_governance_state()
    return {
        "stack": state.stack,
        "phase": state.phase,
        "system_mode": state.system_mode,
        "kill_switch_enabled": state.kill_switch_enabled,
        "broker_orders_enabled": state.broker_orders_enabled,
        "live_trading_enabled": state.live_trading_enabled,
        "canary_trading_enabled": state.canary_trading_enabled,
        "autonomous_runtime_enabled": state.autonomous_runtime_enabled,
        "ai_mutation_enabled": state.ai_mutation_enabled,
        "business_logic_implemented": state.business_logic_implemented,
    }


@router.get("/execution-decision")
def execution_decision() -> dict[str, object]:
    decision = deny_all_execution_in_skeleton()
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }
