from __future__ import annotations

from fastapi import APIRouter

from app.stacks.market_data.services.market_data_service import (
    get_market_data_skeleton_status,
)

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/status")
def market_data_status() -> dict[str, object]:
    status = get_market_data_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "yfinance_adapter_implemented": status.yfinance_adapter_implemented,
        "finnhub_adapter_implemented": status.finnhub_adapter_implemented,
        "live_provider_calls_enabled": status.live_provider_calls_enabled,
        "strategy_logic_implemented": status.strategy_logic_implemented,
        "risk_logic_implemented": status.risk_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
