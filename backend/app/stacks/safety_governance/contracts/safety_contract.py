from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SystemMode(StrEnum):
    OFF = "off"
    RESEARCH_ONLY = "research_only"
    PAPER = "paper"
    BROKER_READ_ONLY = "broker_read_only"
    CANARY = "canary"
    LIVE = "live"


@dataclass(frozen=True)
class SafetyGovernanceStateContract:
    stack: str = "safety_governance"
    phase: str = "phase_3_skeleton"
    system_mode: SystemMode = SystemMode.RESEARCH_ONLY
    kill_switch_enabled: bool = True
    broker_orders_enabled: bool = False
    live_trading_enabled: bool = False
    canary_trading_enabled: bool = False
    autonomous_runtime_enabled: bool = False
    ai_mutation_enabled: bool = False
    business_logic_implemented: bool = False


@dataclass(frozen=True)
class SafetyDecisionContract:
    allowed: bool
    reason: str
