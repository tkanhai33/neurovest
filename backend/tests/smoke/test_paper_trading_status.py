from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperOrderContract,
    PaperOrderSide,
    PaperOrderStatus,
)
from app.stacks.paper_trading.services.paper_trading_service import (
    get_paper_trading_skeleton_status,
    reject_all_paper_orders_in_skeleton,
)


def test_paper_trading_status_is_skeleton_only() -> None:
    status = get_paper_trading_skeleton_status()

    assert status.stack == "paper_trading"
    assert status.phase == "phase_9_skeleton"
    assert status.simulated_order_engine_implemented is False
    assert status.simulated_fill_engine_implemented is False
    assert status.risk_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False


def test_paper_trading_skeleton_rejects_orders() -> None:
    order = PaperOrderContract(
        order_id="order_001",
        symbol="RY.TO",
        side=PaperOrderSide.BUY,
    )

    rejected = reject_all_paper_orders_in_skeleton(order)

    assert rejected.status == PaperOrderStatus.REJECTED
