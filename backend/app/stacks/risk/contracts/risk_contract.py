from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskDecisionStatus(StrEnum):
    NOT_EVALUATED = "not_evaluated"
    REJECTED = "rejected"
    APPROVED_FOR_RESEARCH = "approved_for_research"
    APPROVED_FOR_PAPER = "approved_for_paper"


@dataclass(frozen=True)
class RiskLimitContract:
    max_daily_trades: int
    max_position_percent: float | None = None
    max_daily_drawdown_percent: float | None = None


@dataclass(frozen=True)
class PositionSizingContract:
    symbol: str
    requested_quantity: float | None = None
    approved_quantity: float | None = None


@dataclass(frozen=True)
class RiskDecisionContract:
    candidate_id: str
    status: RiskDecisionStatus = RiskDecisionStatus.NOT_EVALUATED
    reason: str | None = None


@dataclass(frozen=True)
class RiskSkeletonStatus:
    stack: str = "risk"
    phase: str = "phase_8_skeleton"
    position_sizing_implemented: bool = False
    exposure_limits_implemented: bool = False
    drawdown_limits_implemented: bool = False
    daily_trade_limits_implemented: bool = False
    approval_engine_implemented: bool = False
    broker_integration_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    business_logic_implemented: bool = False
