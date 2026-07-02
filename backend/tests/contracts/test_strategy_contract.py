from app.stacks.strategy.contracts.strategy_contract import (
    StrategyCandidateContract,
    StrategyCandidateStatus,
    StrategySignalContract,
    StrategySkeletonStatus,
    StrategyVersionContract,
)


def test_strategy_signal_contract_shape() -> None:
    signal = StrategySignalContract(
        symbol="RY.TO",
        signal_name="placeholder_signal",
        direction=None,
    )

    assert signal.symbol == "RY.TO"
    assert signal.signal_name == "placeholder_signal"
    assert signal.direction is None


def test_strategy_candidate_contract_shape() -> None:
    candidate = StrategyCandidateContract(
        candidate_id="candidate_001",
        strategy_name="placeholder_strategy",
    )

    assert candidate.candidate_id == "candidate_001"
    assert candidate.strategy_name == "placeholder_strategy"
    assert candidate.status == StrategyCandidateStatus.DRAFT


def test_strategy_version_contract_shape() -> None:
    version = StrategyVersionContract(
        strategy_name="placeholder_strategy",
        version="v1",
        parent_version=None,
    )

    assert version.strategy_name == "placeholder_strategy"
    assert version.version == "v1"
    assert version.parent_version is None


def test_strategy_skeleton_status_locked() -> None:
    status = StrategySkeletonStatus()

    assert status.stack == "strategy"
    assert status.phase == "phase_7_skeleton"
    assert status.signal_generation_implemented is False
    assert status.candidate_scoring_implemented is False
    assert status.promotion_logic_implemented is False
    assert status.risk_integration_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False
