from backend.app.stacks.chat_public.execution_state_projection_v26 import (
    render_execution_state,
)
import pytest

@pytest.mark.parametrize("mode,paper,emergency", [
    ("SAFE", False, False),
    ("SIMULATION", True, False),
    ("LOCKED", False, False),
    ("EMERGENCY_STOP", False, True),
])
def test_modes(mode, paper, emergency):
    value = render_execution_state({
        "mode": mode,
        "paper_execution_enabled": paper,
        "live_execution_enabled": False,
        "emergency_stop_active": emergency,
    })
    assert "verification=SERVER_SNAPSHOT_VALIDATED" in value
    assert f"operating_mode={mode}" in value
    assert "paper_trading_supported=YES" in value
    assert "live_execution=NOT_APPROVED" in value
    assert "\\n" not in value
    expected = "CONTROLLER_PERMITS" if paper else "BLOCKED"
    assert f"paper_controller_permission={expected}" in value

@pytest.mark.parametrize("snapshot", [
    None,
    {},
    {"mode": "SIMULATION"},
    {"mode": "SAFE", "paper_execution_enabled": True,
     "live_execution_enabled": False, "emergency_stop_active": False},
    {"mode": "SIMULATION", "paper_execution_enabled": True,
     "live_execution_enabled": True, "emergency_stop_active": False},
    {"mode": "EMERGENCY_STOP", "paper_execution_enabled": False,
     "live_execution_enabled": False, "emergency_stop_active": False},
    {"mode": "UNKNOWN", "paper_execution_enabled": False,
     "live_execution_enabled": False, "emergency_stop_active": False},
])
def test_invalid_snapshot(snapshot):
    value = render_execution_state(snapshot)
    assert "verification=UNAVAILABLE" in value
    assert "paper_controller_permission=UNKNOWN" in value
    assert "live_execution=NOT_APPROVED" in value
