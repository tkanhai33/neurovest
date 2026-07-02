#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/strategy"

echo "========================================="
echo "PHASE 7 - STRATEGY SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/strategy_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StrategyCandidateStatus(StrEnum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    APPROVED_FOR_RESEARCH = "approved_for_research"


@dataclass(frozen=True)
class StrategySignalContract:
    symbol: str
    signal_name: str
    direction: str | None = None


@dataclass(frozen=True)
class StrategyCandidateContract:
    candidate_id: str
    strategy_name: str
    status: StrategyCandidateStatus = StrategyCandidateStatus.DRAFT


@dataclass(frozen=True)
class StrategyVersionContract:
    strategy_name: str
    version: str
    parent_version: str | None = None


@dataclass(frozen=True)
class StrategySkeletonStatus:
    stack: str = "strategy"
    phase: str = "phase_7_skeleton"
    signal_generation_implemented: bool = False
    candidate_scoring_implemented: bool = False
    promotion_logic_implemented: bool = False
    risk_integration_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/strategy_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.strategy.contracts.strategy_contract import (
    StrategySkeletonStatus,
)


def get_strategy_skeleton_status() -> StrategySkeletonStatus:
    return StrategySkeletonStatus()
EOF

cat > "$STACK/api/strategy_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.strategy.services.strategy_service import (
    get_strategy_skeleton_status,
)

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.get("/status")
def strategy_status() -> dict[str, object]:
    status = get_strategy_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "signal_generation_implemented": status.signal_generation_implemented,
        "candidate_scoring_implemented": status.candidate_scoring_implemented,
        "promotion_logic_implemented": status.promotion_logic_implemented,
        "risk_integration_implemented": status.risk_integration_implemented,
        "paper_trading_integration_implemented": status.paper_trading_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Strategy Domain

Phase 7 skeleton only.

Allowed:
- signal contracts
- candidate contracts
- version contracts
- status contract

Forbidden:
- signal generation
- candidate scoring
- strategy optimization
- risk approval
- paper trading execution
- broker interaction
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Strategy Adapters

Phase 7 skeleton only.

No external providers.
No broker adapters.
No execution adapters.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Strategy Stack Tests

Phase 7 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# strategy

Phase 7 — Strategy Skeleton.

Owns:
- strategy signal contracts
- strategy candidate contracts
- strategy version contracts
- future strategy service boundary

Forbidden in Phase 7:
- real signal generation
- candidate scoring
- optimization
- risk approval
- paper trading
- broker interaction
- execution
EOF

cat > "$BACKEND/tests/contracts/test_strategy_contract.py" <<'EOF'
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
EOF

cat > "$BACKEND/tests/smoke/test_strategy_status.py" <<'EOF'
from app.stacks.strategy.services.strategy_service import (
    get_strategy_skeleton_status,
)


def test_strategy_status_is_skeleton_only() -> None:
    status = get_strategy_skeleton_status()

    assert status.stack == "strategy"
    assert status.phase == "phase_7_skeleton"
    assert status.signal_generation_implemented is False
    assert status.candidate_scoring_implemented is False
    assert status.promotion_logic_implemented is False
    assert status.risk_integration_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/architecture/test_strategy_phase_7_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "strategy"

FORBIDDEN_TERMS = [
    "generate_signal",
    "score_candidate",
    "optimize_strategy",
    "risk_approved",
    "submit_order",
    "place_order",
    "execute_trade",
    "paper_trade",
    "broker_client",
]


def test_strategy_phase_7_has_no_strategy_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden strategy implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_7_STRATEGY_SKELETON_CONTRACT.md" <<'EOF'
# Phase 7 Strategy Skeleton Contract

## Status

Phase 7 skeleton only.

## Purpose

Create the strategy stack shape without implementing signal generation, candidate scoring, optimization, risk approval, paper trading, broker interaction, or execution.

## Allowed

- strategy signal contract
- strategy candidate contract
- strategy version contract
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- signal generation
- candidate scoring
- strategy optimization
- strategy promotion implementation
- risk approval
- paper trading
- broker interaction
- execution
- business logic

## Default State

- signal generation implemented: false
- candidate scoring implemented: false
- promotion logic implemented: false
- risk integration implemented: false
- paper trading integration implemented: false
- broker integration implemented: false

## Exit Criteria

- tests pass
- strategy stack has contracts/services/api placeholders
- no signal generation exists
- no scoring exists
- no risk/paper/broker execution exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_7_STRATEGY_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 7 Strategy Skeleton Certification

Status: pending

Checks:
- strategy contract exists
- skeleton service exists
- API placeholder exists
- no signal generation implementation
- no candidate scoring implementation
- no risk approval implementation
- no paper trading implementation
- no broker implementation
- tests pass
EOF

echo
echo "Running Phase 7 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_7_STRATEGY_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 7 Strategy Skeleton Certification

Status: PASS

Checks:
- strategy contract exists
- skeleton service exists
- API placeholder exists
- no signal generation implementation
- no candidate scoring implementation
- no risk approval implementation
- no paper trading implementation
- no broker implementation
- tests pass

Result:
- Phase 7 strategy skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 7 COMPLETE"
echo "========================================="
echo "PASS: Strategy skeleton created and certified."
