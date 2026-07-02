#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/risk"

echo "========================================="
echo "PHASE 8 - RISK SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/risk_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskDecisionStatus(StrEnum):
    NOT_EVALUATED = "not_evaluated"
    REJECTED = "rejected"
    APPROVED_FOR_RESEARCH = "approved_for_research"
    APPROVED_FOR_PAPER = "approved_for_paper"


@dataclass(frozen=True)
class RiskLimitContract:
    max_daily_trades: int
    max_position_percent: float | None = None
    max_daily_drawdown_percent: float | None = None


@dataclass(frozen=True)
class PositionSizingContract:
    symbol: str
    requested_quantity: float | None = None
    approved_quantity: float | None = None


@dataclass(frozen=True)
class RiskDecisionContract:
    candidate_id: str
    status: RiskDecisionStatus = RiskDecisionStatus.NOT_EVALUATED
    reason: str | None = None


@dataclass(frozen=True)
class RiskSkeletonStatus:
    stack: str = "risk"
    phase: str = "phase_8_skeleton"
    position_sizing_implemented: bool = False
    exposure_limits_implemented: bool = False
    drawdown_limits_implemented: bool = False
    daily_trade_limits_implemented: bool = False
    approval_engine_implemented: bool = False
    broker_integration_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/risk_service.py" <<'EOF'
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
EOF

cat > "$STACK/api/risk_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.risk.services.risk_service import (
    deny_all_risk_approval_in_skeleton,
    get_risk_skeleton_status,
)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/status")
def risk_status() -> dict[str, object]:
    status = get_risk_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "position_sizing_implemented": status.position_sizing_implemented,
        "exposure_limits_implemented": status.exposure_limits_implemented,
        "drawdown_limits_implemented": status.drawdown_limits_implemented,
        "daily_trade_limits_implemented": status.daily_trade_limits_implemented,
        "approval_engine_implemented": status.approval_engine_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "paper_trading_integration_implemented": status.paper_trading_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }


@router.get("/approval-decision/{candidate_id}")
def risk_approval_decision(candidate_id: str) -> dict[str, object]:
    decision = deny_all_risk_approval_in_skeleton(candidate_id)
    return {
        "candidate_id": decision.candidate_id,
        "status": decision.status,
        "reason": decision.reason,
    }
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Risk Domain

Phase 8 skeleton only.

Allowed:
- risk limit contracts
- position sizing contracts
- risk decision contracts
- skeleton denial contract
- status contract

Forbidden:
- real position sizing math
- exposure calculations
- drawdown calculations
- daily trade counter logic
- approval engine implementation
- paper trading execution
- broker interaction
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Risk Adapters

Phase 8 skeleton only.

No broker adapters.
No portfolio adapters.
No execution adapters.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Risk Stack Tests

Phase 8 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# risk

Phase 8 — Risk Skeleton.

Owns:
- position sizing contracts
- exposure limit contracts
- drawdown limit contracts
- daily trade limit contracts
- approval/rejection contracts
- future risk service boundary

Forbidden in Phase 8:
- real risk approval
- position sizing math
- exposure calculations
- drawdown calculations
- paper trading
- broker interaction
- execution
EOF

cat > "$BACKEND/tests/contracts/test_risk_contract.py" <<'EOF'
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
EOF

cat > "$BACKEND/tests/smoke/test_risk_status.py" <<'EOF'
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
EOF

cat > "$BACKEND/tests/architecture/test_risk_phase_8_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "risk"

FORBIDDEN_TERMS = [
    "calculate_position_size",
    "calculate_drawdown",
    "calculate_exposure",
    "approve_trade",
    "submit_order",
    "place_order",
    "execute_trade",
    "paper_trade",
    "broker_client",
]


def test_risk_phase_8_has_no_risk_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden risk implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_8_RISK_SKELETON_CONTRACT.md" <<'EOF'
# Phase 8 Risk Skeleton Contract

## Status

Phase 8 skeleton only.

## Purpose

Create the risk stack shape without implementing position sizing, exposure calculations, drawdown calculations, trade approval, paper trading, broker interaction, or execution.

## Allowed

- risk limit contract
- position sizing contract
- risk decision contract
- risk status service
- skeleton denial service
- API placeholder
- tests
- certification artifact

## Forbidden

- position sizing math
- exposure calculations
- drawdown calculations
- daily trade counter implementation
- real trade approval
- paper trading
- broker interaction
- execution
- business logic

## Default State

- position sizing implemented: false
- exposure limits implemented: false
- drawdown limits implemented: false
- daily trade limits implemented: false
- approval engine implemented: false
- broker integration implemented: false
- paper trading integration implemented: false

## Exit Criteria

- tests pass
- risk stack has contracts/services/api placeholders
- all approvals denied
- no risk math exists
- no paper/broker/execution logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_8_RISK_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 8 Risk Skeleton Certification

Status: pending

Checks:
- risk contract exists
- skeleton service exists
- API placeholder exists
- all approvals denied by default
- no position sizing implementation
- no drawdown implementation
- no trade approval implementation
- no paper trading implementation
- no broker implementation
- tests pass
EOF

echo
echo "Running Phase 8 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_8_RISK_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 8 Risk Skeleton Certification

Status: PASS

Checks:
- risk contract exists
- skeleton service exists
- API placeholder exists
- all approvals denied by default
- no position sizing implementation
- no drawdown implementation
- no trade approval implementation
- no paper trading implementation
- no broker implementation
- tests pass

Result:
- Phase 8 risk skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 8 COMPLETE"
echo "========================================="
echo "PASS: Risk skeleton created and certified."
