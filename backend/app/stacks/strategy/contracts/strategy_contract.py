from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StrategyCandidateStatus(StrEnum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    APPROVED_FOR_RESEARCH = "approved_for_research"


@dataclass(frozen=True)
class StrategySignalContract:
    symbol: str
    signal_name: str
    direction: str | None = None


@dataclass(frozen=True)
class StrategyCandidateContract:
    candidate_id: str
    strategy_name: str
    status: StrategyCandidateStatus = StrategyCandidateStatus.DRAFT


@dataclass(frozen=True)
class StrategyVersionContract:
    strategy_name: str
    version: str
    parent_version: str | None = None


@dataclass(frozen=True)
class StrategySkeletonStatus:
    stack: str = "strategy"
    phase: str = "phase_7_skeleton"
    signal_generation_implemented: bool = False
    candidate_scoring_implemented: bool = False
    promotion_logic_implemented: bool = False
    risk_integration_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    business_logic_implemented: bool = False
