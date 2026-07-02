from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperAccountContract,
    PaperFillContract,
    PaperOrderContract,
    PaperOrderSide,
    PaperOrderStatus,
    PaperPnLContract,
    PaperPositionContract,
    PaperTradingSkeletonStatus,
)


def test_paper_account_contract_shape() -> None:
    account = PaperAccountContract(account_id="paper_001", currency="CAD")

    assert account.account_id == "paper_001"
    assert account.currency == "CAD"
    assert account.starting_cash is None


def test_paper_order_contract_shape() -> None:
    order = PaperOrderContract(
        order_id="order_001",
        symbol="RY.TO",
        side=PaperOrderSide.BUY,
    )

    assert order.order_id == "order_001"
    assert order.symbol == "RY.TO"
    assert order.side == PaperOrderSide.BUY
    assert order.status == PaperOrderStatus.DRAFT


def test_paper_fill_contract_shape() -> None:
    fill = PaperFillContract(
        fill_id="fill_001",
        order_id="order_001",
        symbol="RY.TO",
    )

    assert fill.fill_id == "fill_001"
    assert fill.order_id == "order_001"
    assert fill.symbol == "RY.TO"


def test_paper_position_contract_shape() -> None:
    position = PaperPositionContract(symbol="RY.TO")

    assert position.symbol == "RY.TO"
    assert position.quantity is None
    assert position.average_price is None


def test_paper_pnl_contract_shape() -> None:
    pnl = PaperPnLContract(account_id="paper_001")

    assert pnl.account_id == "paper_001"
    assert pnl.realized_pnl is None
    assert pnl.unrealized_pnl is None
    assert pnl.currency == "CAD"


def test_paper_trading_skeleton_status_locked() -> None:
    status = PaperTradingSkeletonStatus()

    assert status.stack == "paper_trading"
    assert status.phase == "phase_9_skeleton"
    assert status.paper_account_implemented is False
    assert status.simulated_order_engine_implemented is False
    assert status.simulated_fill_engine_implemented is False
    assert status.paper_position_logic_implemented is False
    assert status.pnl_logic_implemented is False
    assert status.strategy_integration_implemented is False
    assert status.risk_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False
