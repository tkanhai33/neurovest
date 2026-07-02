from __future__ import annotations

from app.stacks.admin_control.contracts.backend_status_contract import (
    BackendStatusContract,
)


def test_backend_status_contract_is_read_only() -> None:
    status = BackendStatusContract()

    assert status.phase == "phase_37a_read_only_backend_status_contract"
    assert status.read_only is True
    assert status.backend_online is True
    assert status.runtime_enabled is False
    assert status.broker_calls_enabled is False
    assert status.trading_enabled is False
    assert status.mutation_enabled is False
    assert status.provider_calls_enabled is False
    assert status.ai_calls_enabled is False
