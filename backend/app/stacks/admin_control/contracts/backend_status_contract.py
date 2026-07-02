from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendStatusContract:
    stack: str = "admin_control"
    phase: str = "phase_37a_read_only_backend_status_contract"
    read_only: bool = True
    backend_online: bool = True
    runtime_enabled: bool = False
    broker_calls_enabled: bool = False
    trading_enabled: bool = False
    mutation_enabled: bool = False
    provider_calls_enabled: bool = False
    ai_calls_enabled: bool = False
