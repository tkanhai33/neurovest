from __future__ import annotations

from app.stacks.portfolio.contracts.portfolio_contract import (
    PortfolioSkeletonStatus,
)


def get_portfolio_skeleton_status() -> PortfolioSkeletonStatus:
    return PortfolioSkeletonStatus()
