from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StackName(StrEnum):
    IDENTITY_AUTH = "identity_auth"
    SAFETY_GOVERNANCE = "safety_governance"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    RESEARCH = "research"
    STRATEGY = "strategy"
    RISK = "risk"
    PAPER_TRADING = "paper_trading"
    BROKER_INTEGRATION = "broker_integration"
    RUNTIME = "runtime"
    AI_CHAT = "ai_chat"
    ADMIN_CONTROL = "admin_control"


@dataclass(frozen=True)
class StackRegistryEntry:
    name: StackName
    phase: str
    implemented: bool = False
    business_logic_enabled: bool = False


STACK_REGISTRY: tuple[StackRegistryEntry, ...] = (
    StackRegistryEntry(StackName.IDENTITY_AUTH, "phase_2_skeleton"),
    StackRegistryEntry(StackName.SAFETY_GOVERNANCE, "phase_3_skeleton"),
    StackRegistryEntry(StackName.MARKET_DATA, "phase_4_skeleton"),
    StackRegistryEntry(StackName.PORTFOLIO, "phase_5_skeleton"),
    StackRegistryEntry(StackName.RESEARCH, "phase_6_skeleton"),
    StackRegistryEntry(StackName.STRATEGY, "phase_7_skeleton"),
    StackRegistryEntry(StackName.RISK, "phase_8_skeleton"),
    StackRegistryEntry(StackName.PAPER_TRADING, "phase_9_skeleton"),
    StackRegistryEntry(StackName.BROKER_INTEGRATION, "phase_10_skeleton"),
    StackRegistryEntry(StackName.RUNTIME, "phase_11_skeleton"),
    StackRegistryEntry(StackName.AI_CHAT, "phase_12_skeleton"),
    StackRegistryEntry(StackName.ADMIN_CONTROL, "phase_0_skeleton"),
)
