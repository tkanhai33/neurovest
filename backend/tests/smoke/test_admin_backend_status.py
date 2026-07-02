from __future__ import annotations

from app.stacks.admin_control.api.admin_control_routes import backend_status


def test_admin_backend_status_route_is_read_only() -> None:
    status = backend_status()

    assert status["phase"] == "phase_37a_read_only_backend_status_contract"
    assert status["read_only"] is True
    assert status["runtime_enabled"] is False
    assert status["broker_calls_enabled"] is False
    assert status["trading_enabled"] is False
    assert status["mutation_enabled"] is False
