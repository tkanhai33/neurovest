from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoldingContract:
    symbol: str
    quantity: float | None = None
    average_cost: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class BalanceContract:
    cash: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class PortfolioSnapshotContract:
    portfolio_id: str
    holdings_count: int = 0
    total_value: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class PortfolioSkeletonStatus:
    stack: str = "portfolio"
    phase: str = "phase_5_skeleton"
    broker_read_implemented: bool = False
    portfolio_mutation_implemented: bool = False
    transaction_logic_implemented: bool = False
    performance_logic_implemented: bool = False
    business_logic_implemented: bool = False
