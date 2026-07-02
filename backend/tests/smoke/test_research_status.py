from app.stacks.research.services.research_service import (
    get_research_skeleton_status,
)


def test_research_status_is_skeleton_only() -> None:
    status = get_research_skeleton_status()

    assert status.stack == "research"
    assert status.phase == "phase_6_skeleton"
    assert status.indicators_implemented is False
    assert status.screeners_implemented is False
    assert status.backtests_implemented is False
    assert status.news_analysis_implemented is False
    assert status.market_data_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.trading_logic_implemented is False
    assert status.business_logic_implemented is False
