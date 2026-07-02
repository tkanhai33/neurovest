from __future__ import annotations

from app.stacks.safety_governance.contracts.safety_contract import (
    SafetyDecisionContract,
    SafetyGovernanceStateContract,
)


def get_safety_governance_state() -> SafetyGovernanceStateContract:
    return SafetyGovernanceStateContract()


def deny_all_execution_in_skeleton() -> SafetyDecisionContract:
    return SafetyDecisionContract(
        allowed=False,
        reason="Phase 3 skeleton denies all execution paths.",
    )
