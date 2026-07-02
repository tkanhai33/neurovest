from __future__ import annotations

from app.stacks.strategy.contracts.strategy_contract import (
    StrategySkeletonStatus,
)


def get_strategy_skeleton_status() -> StrategySkeletonStatus:
    return StrategySkeletonStatus()
