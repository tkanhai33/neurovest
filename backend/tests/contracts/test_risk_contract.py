from app.stacks.risk.contracts.risk_contract import (
    PositionSizingContract,
    RiskDecisionContract,
    RiskDecisionStatus,
    RiskLimitContract,
    RiskSkeletonStatus,
)


def test_risk_limit_contract_shape() -> None:
    limits = RiskLimitContract(
        max_daily_trades=10,
        max_position_percent=None,
        max_daily_drawdown_percent=None,
    )

    assert limits.max_daily_trades == 10
    assert limits.max_position_percent is None
    assert limits.max_daily_drawdown_percent is None


def test_position_sizing_contract_shape() -> None:
    sizing = PositionSizingContract(
        symbol="RY.TO",
        requested_quantity=None,
        approved_quantity=None,
    )

    assert sizing.symbol == "RY.TO"
    assert sizing.requested_quantity is None
    assert sizing.approved_quantity is None


def test_risk_decision_contract_shape() -> None:
    decision = RiskDecisionContract(candidate_id="candidate_001")

    assert decision.candidate_id == "candidate_001"
    assert decision.status == RiskDecisionStatus.NOT_EVALUATED
    assert decision.reason is None


def test_risk_skeleton_status_locked() -> None:
    status = RiskSkeletonStatus()

    assert status.stack == "risk"
    assert status.phase == "phase_8_skeleton"
    assert status.position_sizing_implemented is False
    assert status.exposure_limits_implemented is False
    assert status.drawdown_limits_implemented is False
    assert status.daily_trade_limits_implemented is False
    assert status.approval_engine_implemented is False
    assert status.broker_integration_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.business_logic_implemented is False
