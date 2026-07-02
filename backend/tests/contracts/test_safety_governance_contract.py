from app.stacks.safety_governance.contracts.safety_contract import (
    SafetyDecisionContract,
    SafetyGovernanceStateContract,
    SystemMode,
)


def test_safety_governance_default_state_locked() -> None:
    state = SafetyGovernanceStateContract()

    assert state.stack == "safety_governance"
    assert state.phase == "phase_3_skeleton"
    assert state.system_mode == SystemMode.RESEARCH_ONLY
    assert state.kill_switch_enabled is True
    assert state.broker_orders_enabled is False
    assert state.live_trading_enabled is False
    assert state.canary_trading_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False
    assert state.business_logic_implemented is False


def test_safety_decision_contract_shape() -> None:
    decision = SafetyDecisionContract(allowed=False, reason="locked")

    assert decision.allowed is False
    assert decision.reason == "locked"
