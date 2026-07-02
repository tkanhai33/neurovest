from __future__ import annotations

from fastapi import APIRouter

from app.stacks.risk.services.risk_service import (
    deny_all_risk_approval_in_skeleton,
    get_risk_skeleton_status,
)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/status")
def risk_status() -> dict[str, object]:
    status = get_risk_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "position_sizing_implemented": status.position_sizing_implemented,
        "exposure_limits_implemented": status.exposure_limits_implemented,
        "drawdown_limits_implemented": status.drawdown_limits_implemented,
        "daily_trade_limits_implemented": status.daily_trade_limits_implemented,
        "approval_engine_implemented": status.approval_engine_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "paper_trading_integration_implemented": status.paper_trading_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }


@router.get("/approval-decision/{candidate_id}")
def risk_approval_decision(candidate_id: str) -> dict[str, object]:
    decision = deny_all_risk_approval_in_skeleton(candidate_id)
    return {
        "candidate_id": decision.candidate_id,
        "status": decision.status,
        "reason": decision.reason,
    }
