from app.stacks.safety_governance.services.safety_governance_service import (
    deny_all_execution_in_skeleton,
    get_safety_governance_state,
)


def test_safety_governance_status_is_locked() -> None:
    state = get_safety_governance_state()

    assert state.kill_switch_enabled is True
    assert state.broker_orders_enabled is False
    assert state.live_trading_enabled is False
    assert state.canary_trading_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False


def test_safety_governance_denies_execution() -> None:
    decision = deny_all_execution_in_skeleton()

    assert decision.allowed is False
    assert "denies all execution" in decision.reason
