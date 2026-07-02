from app.stacks.risk.contracts.risk_contract import RiskDecisionStatus
from app.stacks.risk.services.risk_service import (
    deny_all_risk_approval_in_skeleton,
    get_risk_skeleton_status,
)


def test_risk_status_is_skeleton_only() -> None:
    status = get_risk_skeleton_status()

    assert status.stack == "risk"
    assert status.phase == "phase_8_skeleton"
    assert status.position_sizing_implemented is False
    assert status.approval_engine_implemented is False
    assert status.broker_integration_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.business_logic_implemented is False


def test_risk_skeleton_denies_all_approval() -> None:
    decision = deny_all_risk_approval_in_skeleton("candidate_001")

    assert decision.candidate_id == "candidate_001"
    assert decision.status == RiskDecisionStatus.REJECTED
    assert "denies all risk approvals" in str(decision.reason)
