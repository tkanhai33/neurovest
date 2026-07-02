from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemState:
    project: str = "NeuroVest"
    phase: str = "phase_12a_global_registry_skeleton"
    foundation_certified: bool = True
    skeletons_certified: bool = True
    business_logic_enabled: bool = False
    live_trading_enabled: bool = False
    broker_orders_enabled: bool = False
    autonomous_runtime_enabled: bool = False
    ai_mutation_enabled: bool = False


def get_system_state() -> SystemState:
    return SystemState()
