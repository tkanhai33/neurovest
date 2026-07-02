from app.stacks.strategy.services.strategy_service import (
    get_strategy_skeleton_status,
)


def test_strategy_status_is_skeleton_only() -> None:
    status = get_strategy_skeleton_status()

    assert status.stack == "strategy"
    assert status.phase == "phase_7_skeleton"
    assert status.signal_generation_implemented is False
    assert status.candidate_scoring_implemented is False
    assert status.promotion_logic_implemented is False
    assert status.risk_integration_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False
