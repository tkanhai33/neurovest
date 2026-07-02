from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RuntimeWorkflowStatus(StrEnum):
    DISABLED = "disabled"
    SKELETON_ONLY = "skeleton_only"
    READY_FOR_REVIEW = "ready_for_review"


class RuntimeJobType(StrEnum):
    MANUAL_RESEARCH_REFRESH = "manual_research_refresh"
    MANUAL_PORTFOLIO_REFRESH = "manual_portfolio_refresh"
    MANUAL_PAPER_REVIEW = "manual_paper_review"


@dataclass(frozen=True)
class RuntimeWorkflowContract:
    workflow_id: str
    job_type: RuntimeJobType
    status: RuntimeWorkflowStatus = RuntimeWorkflowStatus.DISABLED


@dataclass(frozen=True)
class RuntimeScheduleContract:
    schedule_id: str
    workflow_id: str
    enabled: bool = False


@dataclass(frozen=True)
class RuntimeEventContract:
    event_id: str
    workflow_id: str
    event_name: str


@dataclass(frozen=True)
class RuntimeSkeletonStatus:
    stack: str = "runtime"
    phase: str = "phase_11_skeleton"
    scheduler_implemented: bool = False
    background_loops_enabled: bool = False
    workflow_execution_implemented: bool = False
    strategy_execution_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    mutation_logic_implemented: bool = False
    business_logic_implemented: bool = False
