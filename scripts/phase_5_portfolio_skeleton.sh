#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/portfolio"

echo "========================================="
echo "PHASE 5 - PORTFOLIO SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/portfolio_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoldingContract:
    symbol: str
    quantity: float | None = None
    average_cost: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class BalanceContract:
    cash: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class PortfolioSnapshotContract:
    portfolio_id: str
    holdings_count: int = 0
    total_value: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class PortfolioSkeletonStatus:
    stack: str = "portfolio"
    phase: str = "phase_5_skeleton"
    broker_read_implemented: bool = False
    portfolio_mutation_implemented: bool = False
    transaction_logic_implemented: bool = False
    performance_logic_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/portfolio_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.portfolio.contracts.portfolio_contract import (
    PortfolioSkeletonStatus,
)


def get_portfolio_skeleton_status() -> PortfolioSkeletonStatus:
    return PortfolioSkeletonStatus()
EOF

cat > "$STACK/api/portfolio_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.portfolio.services.portfolio_service import (
    get_portfolio_skeleton_status,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/status")
def portfolio_status() -> dict[str, object]:
    status = get_portfolio_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "broker_read_implemented": status.broker_read_implemented,
        "portfolio_mutation_implemented": status.portfolio_mutation_implemented,
        "transaction_logic_implemented": status.transaction_logic_implemented,
        "performance_logic_implemented": status.performance_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Portfolio Adapters

Phase 5 skeleton only.

Forbidden:
- broker account reads
- broker provider calls
- portfolio mutation
- transaction imports
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Portfolio Domain

Phase 5 skeleton only.

Allowed:
- holding contract
- balance contract
- portfolio snapshot contract
- status contract

Forbidden:
- broker reads
- live account sync
- transaction logic
- performance calculations
- portfolio mutation
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Portfolio Stack Tests

Phase 5 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# portfolio

Phase 5 — Portfolio Skeleton.

Owns:
- holdings contracts
- balance contracts
- snapshot contracts
- future portfolio read boundary

Forbidden in Phase 5:
- broker account reads
- portfolio mutation
- transaction logic
- performance calculations
- trading logic
EOF

cat > "$BACKEND/tests/contracts/test_portfolio_contract.py" <<'EOF'
from app.stacks.portfolio.contracts.portfolio_contract import (
    BalanceContract,
    HoldingContract,
    PortfolioSkeletonStatus,
    PortfolioSnapshotContract,
)


def test_holding_contract_shape() -> None:
    holding = HoldingContract(symbol="RY.TO", quantity=None, average_cost=None, currency="CAD")

    assert holding.symbol == "RY.TO"
    assert holding.quantity is None
    assert holding.average_cost is None
    assert holding.currency == "CAD"


def test_balance_contract_shape() -> None:
    balance = BalanceContract(cash=None, currency="CAD")

    assert balance.cash is None
    assert balance.currency == "CAD"


def test_portfolio_snapshot_contract_shape() -> None:
    snapshot = PortfolioSnapshotContract(
        portfolio_id="portfolio_001",
        holdings_count=0,
        total_value=None,
        currency="CAD",
    )

    assert snapshot.portfolio_id == "portfolio_001"
    assert snapshot.holdings_count == 0
    assert snapshot.total_value is None
    assert snapshot.currency == "CAD"


def test_portfolio_skeleton_status_locked() -> None:
    status = PortfolioSkeletonStatus()

    assert status.stack == "portfolio"
    assert status.phase == "phase_5_skeleton"
    assert status.broker_read_implemented is False
    assert status.portfolio_mutation_implemented is False
    assert status.transaction_logic_implemented is False
    assert status.performance_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_portfolio_status.py" <<'EOF'
from app.stacks.portfolio.services.portfolio_service import (
    get_portfolio_skeleton_status,
)


def test_portfolio_status_is_skeleton_only() -> None:
    status = get_portfolio_skeleton_status()

    assert status.stack == "portfolio"
    assert status.phase == "phase_5_skeleton"
    assert status.broker_read_implemented is False
    assert status.portfolio_mutation_implemented is False
    assert status.transaction_logic_implemented is False
    assert status.performance_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/architecture/test_portfolio_phase_5_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "portfolio"

FORBIDDEN_TERMS = [
    "import snaptrade",
    "submit_order",
    "place_order",
    "execute_trade",
    "sync_broker_account",
    "broker_client",
    "calculate_performance",
    "mutate_portfolio",
]


def test_portfolio_phase_5_has_no_broker_or_mutation_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden portfolio implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_5_PORTFOLIO_SKELETON_CONTRACT.md" <<'EOF'
# Phase 5 Portfolio Skeleton Contract

## Status

Phase 5 skeleton only.

## Purpose

Create the portfolio stack shape without implementing broker reads, transactions, performance logic, or portfolio mutation.

## Allowed

- holding contract
- balance contract
- portfolio snapshot contract
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- broker account reads
- broker provider calls
- transaction imports
- portfolio mutation
- performance calculations
- trading logic
- business logic

## Default State

- broker read implemented: false
- portfolio mutation implemented: false
- transaction logic implemented: false
- performance logic implemented: false

## Exit Criteria

- tests pass
- portfolio stack has contracts/services/api placeholders
- no broker read implementation exists
- no portfolio mutation exists
- no performance logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_5_PORTFOLIO_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 5 Portfolio Skeleton Certification

Status: pending

Checks:
- portfolio contract exists
- skeleton service exists
- API placeholder exists
- no broker read implementation
- no portfolio mutation implementation
- no performance logic implementation
- tests pass
EOF

echo
echo "Running Phase 5 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_5_PORTFOLIO_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 5 Portfolio Skeleton Certification

Status: PASS

Checks:
- portfolio contract exists
- skeleton service exists
- API placeholder exists
- no broker read implementation
- no portfolio mutation implementation
- no performance logic implementation
- tests pass

Result:
- Phase 5 portfolio skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 5 COMPLETE"
echo "========================================="
echo "PASS: Portfolio skeleton created and certified."
