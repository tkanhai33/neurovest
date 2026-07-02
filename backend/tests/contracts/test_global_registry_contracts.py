from app.shared.contracts.feature_registry import FEATURE_FLAGS
from app.shared.contracts.phase_registry import PHASE_REGISTRY
from app.shared.contracts.stack_registry import STACK_REGISTRY, StackName
from app.shared.contracts.system_state import get_system_state


def test_stack_registry_contains_core_stacks() -> None:
    names = {entry.name for entry in STACK_REGISTRY}

    assert StackName.IDENTITY_AUTH in names
    assert StackName.SAFETY_GOVERNANCE in names
    assert StackName.MARKET_DATA in names
    assert StackName.PORTFOLIO in names
    assert StackName.RESEARCH in names
    assert StackName.STRATEGY in names
    assert StackName.RISK in names
    assert StackName.PAPER_TRADING in names
    assert StackName.BROKER_INTEGRATION in names
    assert StackName.RUNTIME in names
    assert StackName.AI_CHAT in names


def test_stack_registry_business_logic_disabled() -> None:
    assert all(entry.business_logic_enabled is False for entry in STACK_REGISTRY)


def test_phase_registry_contains_phase_12a() -> None:
    phases = {entry.phase for entry in PHASE_REGISTRY}

    assert "phase_12a" in phases


def test_feature_flags_disabled_by_default() -> None:
    assert FEATURE_FLAGS
    assert all(flag.enabled is False for flag in FEATURE_FLAGS)


def test_system_state_locked() -> None:
    state = get_system_state()

    assert state.project == "NeuroVest"
    assert state.foundation_certified is True
    assert state.skeletons_certified is True
    assert state.business_logic_enabled is False
    assert state.live_trading_enabled is False
    assert state.broker_orders_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False
