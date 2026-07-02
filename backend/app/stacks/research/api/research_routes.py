from __future__ import annotations

from fastapi import APIRouter

from app.stacks.research.services.research_service import (
    get_research_skeleton_status,
)

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/status")
def research_status() -> dict[str, object]:
    status = get_research_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "indicators_implemented": status.indicators_implemented,
        "screeners_implemented": status.screeners_implemented,
        "backtests_implemented": status.backtests_implemented,
        "news_analysis_implemented": status.news_analysis_implemented,
        "market_data_calls_enabled": status.market_data_calls_enabled,
        "strategy_logic_implemented": status.strategy_logic_implemented,
        "trading_logic_implemented": status.trading_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
