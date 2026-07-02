from __future__ import annotations

from fastapi import APIRouter

from app.stacks.paper_trading.services.paper_trading_service import (
    get_paper_trading_skeleton_status,
)

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])


@router.get("/status")
def paper_trading_status() -> dict[str, object]:
    status = get_paper_trading_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "paper_account_implemented": status.paper_account_implemented,
        "simulated_order_engine_implemented": status.simulated_order_engine_implemented,
        "simulated_fill_engine_implemented": status.simulated_fill_engine_implemented,
        "paper_position_logic_implemented": status.paper_position_logic_implemented,
        "pnl_logic_implemented": status.pnl_logic_implemented,
        "strategy_integration_implemented": status.strategy_integration_implemented,
        "risk_integration_implemented": status.risk_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
