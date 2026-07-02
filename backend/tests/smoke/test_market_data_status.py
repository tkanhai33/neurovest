from app.stacks.market_data.adapters.finnhub_adapter import (
    finnhub_adapter_placeholder,
)
from app.stacks.market_data.adapters.yfinance_adapter import (
    yfinance_adapter_placeholder,
)
from app.stacks.market_data.services.market_data_service import (
    get_market_data_skeleton_status,
)


def test_market_data_status_is_skeleton_only() -> None:
    status = get_market_data_skeleton_status()

    assert status.stack == "market_data"
    assert status.phase == "phase_4_skeleton"
    assert status.live_provider_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.risk_logic_implemented is False
    assert status.business_logic_implemented is False


def test_market_data_provider_placeholders_do_not_call_network() -> None:
    assert yfinance_adapter_placeholder() == "phase_4_skeleton_only_no_provider_calls"
    assert finnhub_adapter_placeholder() == "phase_4_skeleton_only_no_provider_calls"
