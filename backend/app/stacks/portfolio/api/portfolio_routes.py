from __future__ import annotations

from fastapi import APIRouter

from app.stacks.portfolio.services.portfolio_service import (
    get_portfolio_skeleton_status,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/status")
def portfolio_status() -> dict[str, object]:
    status = get_portfolio_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "broker_read_implemented": status.broker_read_implemented,
        "portfolio_mutation_implemented": status.portfolio_mutation_implemented,
        "transaction_logic_implemented": status.transaction_logic_implemented,
        "performance_logic_implemented": status.performance_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
