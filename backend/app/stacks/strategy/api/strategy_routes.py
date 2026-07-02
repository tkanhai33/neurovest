from __future__ import annotations

from fastapi import APIRouter

from app.stacks.strategy.services.strategy_service import (
    get_strategy_skeleton_status,
)

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.get("/status")
def strategy_status() -> dict[str, object]:
    status = get_strategy_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "signal_generation_implemented": status.signal_generation_implemented,
        "candidate_scoring_implemented": status.candidate_scoring_implemented,
        "promotion_logic_implemented": status.promotion_logic_implemented,
        "risk_integration_implemented": status.risk_integration_implemented,
        "paper_trading_integration_implemented": status.paper_trading_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
