from app.stacks.portfolio.contracts.portfolio_contract import (
    BalanceContract,
    HoldingContract,
    PortfolioSkeletonStatus,
    PortfolioSnapshotContract,
)


def test_holding_contract_shape() -> None:
    holding = HoldingContract(symbol="RY.TO", quantity=None, average_cost=None, currency="CAD")

    assert holding.symbol == "RY.TO"
    assert holding.quantity is None
    assert holding.average_cost is None
    assert holding.currency == "CAD"


def test_balance_contract_shape() -> None:
    balance = BalanceContract(cash=None, currency="CAD")

    assert balance.cash is None
    assert balance.currency == "CAD"


def test_portfolio_snapshot_contract_shape() -> None:
    snapshot = PortfolioSnapshotContract(
        portfolio_id="portfolio_001",
        holdings_count=0,
        total_value=None,
        currency="CAD",
    )

    assert snapshot.portfolio_id == "portfolio_001"
    assert snapshot.holdings_count == 0
    assert snapshot.total_value is None
    assert snapshot.currency == "CAD"


def test_portfolio_skeleton_status_locked() -> None:
    status = PortfolioSkeletonStatus()

    assert status.stack == "portfolio"
    assert status.phase == "phase_5_skeleton"
    assert status.broker_read_implemented is False
    assert status.portfolio_mutation_implemented is False
    assert status.transaction_logic_implemented is False
    assert status.performance_logic_implemented is False
    assert status.business_logic_implemented is False
