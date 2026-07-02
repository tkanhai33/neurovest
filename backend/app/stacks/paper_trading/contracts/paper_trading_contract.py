from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaperOrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class PaperOrderStatus(StrEnum):
    DRAFT = "draft"
    REJECTED = "rejected"
    SIMULATION_PENDING = "simulation_pending"
    SIMULATED = "simulated"


@dataclass(frozen=True)
class PaperAccountContract:
    account_id: str
    currency: str = "CAD"
    starting_cash: float | None = None


@dataclass(frozen=True)
class PaperOrderContract:
    order_id: str
    symbol: str
    side: PaperOrderSide
    quantity: float | None = None
    status: PaperOrderStatus = PaperOrderStatus.DRAFT


@dataclass(frozen=True)
class PaperFillContract:
    fill_id: str
    order_id: str
    symbol: str
    filled_quantity: float | None = None
    fill_price: float | None = None


@dataclass(frozen=True)
class PaperPositionContract:
    symbol: str
    quantity: float | None = None
    average_price: float | None = None


@dataclass(frozen=True)
class PaperPnLContract:
    account_id: str
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None
    currency: str = "CAD"


@dataclass(frozen=True)
class PaperTradingSkeletonStatus:
    stack: str = "paper_trading"
    phase: str = "phase_9_skeleton"
    paper_account_implemented: bool = False
    simulated_order_engine_implemented: bool = False
    simulated_fill_engine_implemented: bool = False
    paper_position_logic_implemented: bool = False
    pnl_logic_implemented: bool = False
    strategy_integration_implemented: bool = False
    risk_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    business_logic_implemented: bool = False
