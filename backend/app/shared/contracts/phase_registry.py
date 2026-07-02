from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseRegistryEntry:
    phase: str
    name: str
    status: str


PHASE_REGISTRY: tuple[PhaseRegistryEntry, ...] = (
    PhaseRegistryEntry("phase_1", "foundation", "certified"),
    PhaseRegistryEntry("phase_2", "identity_auth_skeleton", "certified"),
    PhaseRegistryEntry("phase_3", "safety_governance_skeleton", "certified"),
    PhaseRegistryEntry("phase_4", "market_data_skeleton", "certified"),
    PhaseRegistryEntry("phase_5", "portfolio_skeleton", "certified"),
    PhaseRegistryEntry("phase_6", "research_skeleton", "certified"),
    PhaseRegistryEntry("phase_7", "strategy_skeleton", "certified"),
    PhaseRegistryEntry("phase_8", "risk_skeleton", "certified"),
    PhaseRegistryEntry("phase_9", "paper_trading_skeleton", "certified"),
    PhaseRegistryEntry("phase_10", "broker_integration_skeleton", "certified"),
    PhaseRegistryEntry("phase_11", "runtime_skeleton", "certified"),
    PhaseRegistryEntry("phase_12", "ai_chat_skeleton", "certified"),
    PhaseRegistryEntry("phase_12a", "global_registry_skeleton", "skeleton"),
)
