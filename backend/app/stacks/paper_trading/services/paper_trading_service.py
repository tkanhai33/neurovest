from __future__ import annotations

from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperOrderContract,
    PaperOrderStatus,
    PaperTradingSkeletonStatus,
)


def get_paper_trading_skeleton_status() -> PaperTradingSkeletonStatus:
    return PaperTradingSkeletonStatus()


def reject_all_paper_orders_in_skeleton(order: PaperOrderContract) -> PaperOrderContract:
    return PaperOrderContract(
        order_id=order.order_id,
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        status=PaperOrderStatus.REJECTED,
    )
