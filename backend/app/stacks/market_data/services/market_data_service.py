from __future__ import annotations

from app.stacks.market_data.contracts.market_data_contract import (
    MarketDataSkeletonStatus,
)


def get_market_data_skeleton_status() -> MarketDataSkeletonStatus:
    return MarketDataSkeletonStatus()
