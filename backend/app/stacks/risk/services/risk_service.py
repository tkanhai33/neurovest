from __future__ import annotations

from app.stacks.risk.contracts.risk_contract import (
    RiskDecisionContract,
    RiskDecisionStatus,
    RiskSkeletonStatus,
)


def get_risk_skeleton_status() -> RiskSkeletonStatus:
    return RiskSkeletonStatus()


def deny_all_risk_approval_in_skeleton(candidate_id: str) -> RiskDecisionContract:
    return RiskDecisionContract(
        candidate_id=candidate_id,
        status=RiskDecisionStatus.REJECTED,
        reason="Phase 8 skeleton denies all risk approvals.",
    )
