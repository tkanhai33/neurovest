from app.stacks.portfolio.services.portfolio_service import (
    get_portfolio_skeleton_status,
)


def test_portfolio_status_is_skeleton_only() -> None:
    status = get_portfolio_skeleton_status()

    assert status.stack == "portfolio"
    assert status.phase == "phase_5_skeleton"
    assert status.broker_read_implemented is False
    assert status.portfolio_mutation_implemented is False
    assert status.transaction_logic_implemented is False
    assert status.performance_logic_implemented is False
    assert status.business_logic_implemented is False
