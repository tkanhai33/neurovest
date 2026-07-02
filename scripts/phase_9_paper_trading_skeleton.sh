#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/paper_trading"

echo "========================================="
echo "PHASE 9 - PAPER TRADING SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/paper_trading_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaperOrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class PaperOrderStatus(StrEnum):
    DRAFT = "draft"
    REJECTED = "rejected"
    SIMULATION_PENDING = "simulation_pending"
    SIMULATED = "simulated"


@dataclass(frozen=True)
class PaperAccountContract:
    account_id: str
    currency: str = "CAD"
    starting_cash: float | None = None


@dataclass(frozen=True)
class PaperOrderContract:
    order_id: str
    symbol: str
    side: PaperOrderSide
    quantity: float | None = None
    status: PaperOrderStatus = PaperOrderStatus.DRAFT


@dataclass(frozen=True)
class PaperFillContract:
    fill_id: str
    order_id: str
    symbol: str
    filled_quantity: float | None = None
    fill_price: float | None = None


@dataclass(frozen=True)
class PaperPositionContract:
    symbol: str
    quantity: float | None = None
    average_price: float | None = None


@dataclass(frozen=True)
class PaperPnLContract:
    account_id: str
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None
    currency: str = "CAD"


@dataclass(frozen=True)
class PaperTradingSkeletonStatus:
    stack: str = "paper_trading"
    phase: str = "phase_9_skeleton"
    paper_account_implemented: bool = False
    simulated_order_engine_implemented: bool = False
    simulated_fill_engine_implemented: bool = False
    paper_position_logic_implemented: bool = False
    pnl_logic_implemented: bool = False
    strategy_integration_implemented: bool = False
    risk_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/paper_trading_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperOrderContract,
    PaperOrderStatus,
    PaperTradingSkeletonStatus,
)


def get_paper_trading_skeleton_status() -> PaperTradingSkeletonStatus:
    return PaperTradingSkeletonStatus()


def reject_all_paper_orders_in_skeleton(order: PaperOrderContract) -> PaperOrderContract:
    return PaperOrderContract(
        order_id=order.order_id,
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        status=PaperOrderStatus.REJECTED,
    )
EOF

cat > "$STACK/api/paper_trading_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.paper_trading.services.paper_trading_service import (
    get_paper_trading_skeleton_status,
)

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])


@router.get("/status")
def paper_trading_status() -> dict[str, object]:
    status = get_paper_trading_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "paper_account_implemented": status.paper_account_implemented,
        "simulated_order_engine_implemented": status.simulated_order_engine_implemented,
        "simulated_fill_engine_implemented": status.simulated_fill_engine_implemented,
        "paper_position_logic_implemented": status.paper_position_logic_implemented,
        "pnl_logic_implemented": status.pnl_logic_implemented,
        "strategy_integration_implemented": status.strategy_integration_implemented,
        "risk_integration_implemented": status.risk_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Paper Trading Domain

Phase 9 skeleton only.

Allowed:
- paper account contracts
- paper order contracts
- paper fill contracts
- paper position contracts
- paper PnL contracts
- skeleton rejection status

Forbidden:
- simulated order engine
- simulated fill engine
- position mutation
- PnL calculations
- strategy integration
- risk integration
- broker interaction
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Paper Trading Adapters

Phase 9 skeleton only.

No broker adapters.
No market data adapters.
No execution adapters.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Paper Trading Stack Tests

Phase 9 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# paper_trading

Phase 9 — Paper Trading Skeleton.

Owns:
- paper account contracts
- simulated order contracts
- simulated fill contracts
- paper position contracts
- paper PnL contracts
- future paper trading service boundary

Forbidden in Phase 9:
- fill engine
- execution engine
- strategy integration
- risk integration
- broker interaction
- portfolio mutation
- real money movement
EOF

cat > "$BACKEND/tests/contracts/test_paper_trading_contract.py" <<'EOF'
from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperAccountContract,
    PaperFillContract,
    PaperOrderContract,
    PaperOrderSide,
    PaperOrderStatus,
    PaperPnLContract,
    PaperPositionContract,
    PaperTradingSkeletonStatus,
)


def test_paper_account_contract_shape() -> None:
    account = PaperAccountContract(account_id="paper_001", currency="CAD")

    assert account.account_id == "paper_001"
    assert account.currency == "CAD"
    assert account.starting_cash is None


def test_paper_order_contract_shape() -> None:
    order = PaperOrderContract(
        order_id="order_001",
        symbol="RY.TO",
        side=PaperOrderSide.BUY,
    )

    assert order.order_id == "order_001"
    assert order.symbol == "RY.TO"
    assert order.side == PaperOrderSide.BUY
    assert order.status == PaperOrderStatus.DRAFT


def test_paper_fill_contract_shape() -> None:
    fill = PaperFillContract(
        fill_id="fill_001",
        order_id="order_001",
        symbol="RY.TO",
    )

    assert fill.fill_id == "fill_001"
    assert fill.order_id == "order_001"
    assert fill.symbol == "RY.TO"


def test_paper_position_contract_shape() -> None:
    position = PaperPositionContract(symbol="RY.TO")

    assert position.symbol == "RY.TO"
    assert position.quantity is None
    assert position.average_price is None


def test_paper_pnl_contract_shape() -> None:
    pnl = PaperPnLContract(account_id="paper_001")

    assert pnl.account_id == "paper_001"
    assert pnl.realized_pnl is None
    assert pnl.unrealized_pnl is None
    assert pnl.currency == "CAD"


def test_paper_trading_skeleton_status_locked() -> None:
    status = PaperTradingSkeletonStatus()

    assert status.stack == "paper_trading"
    assert status.phase == "phase_9_skeleton"
    assert status.paper_account_implemented is False
    assert status.simulated_order_engine_implemented is False
    assert status.simulated_fill_engine_implemented is False
    assert status.paper_position_logic_implemented is False
    assert status.pnl_logic_implemented is False
    assert status.strategy_integration_implemented is False
    assert status.risk_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_paper_trading_status.py" <<'EOF'
from app.stacks.paper_trading.contracts.paper_trading_contract import (
    PaperOrderContract,
    PaperOrderSide,
    PaperOrderStatus,
)
from app.stacks.paper_trading.services.paper_trading_service import (
    get_paper_trading_skeleton_status,
    reject_all_paper_orders_in_skeleton,
)


def test_paper_trading_status_is_skeleton_only() -> None:
    status = get_paper_trading_skeleton_status()

    assert status.stack == "paper_trading"
    assert status.phase == "phase_9_skeleton"
    assert status.simulated_order_engine_implemented is False
    assert status.simulated_fill_engine_implemented is False
    assert status.risk_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.business_logic_implemented is False


def test_paper_trading_skeleton_rejects_orders() -> None:
    order = PaperOrderContract(
        order_id="order_001",
        symbol="RY.TO",
        side=PaperOrderSide.BUY,
    )

    rejected = reject_all_paper_orders_in_skeleton(order)

    assert rejected.status == PaperOrderStatus.REJECTED
EOF

cat > "$BACKEND/tests/architecture/test_paper_trading_phase_9_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "paper_trading"

FORBIDDEN_TERMS = [
    "simulate_fill",
    "match_order",
    "calculate_pnl",
    "update_position",
    "submit_order",
    "place_order",
    "execute_trade",
    "broker_client",
    "risk_approved",
    "strategy_signal",
]


def test_paper_trading_phase_9_has_no_execution_or_integration_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden paper trading implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_9_PAPER_TRADING_SKELETON_CONTRACT.md" <<'EOF'
# Phase 9 Paper Trading Skeleton Contract

## Status

Phase 9 skeleton only.

## Purpose

Create the paper trading stack shape without implementing simulated fills, position mutation, PnL calculations, strategy integration, risk integration, broker interaction, or execution.

## Allowed

- paper account contract
- paper order contract
- paper fill contract
- paper position contract
- paper PnL contract
- skeleton rejection service
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- simulated order engine
- simulated fill engine
- position mutation
- PnL calculations
- strategy integration
- risk integration
- broker interaction
- execution
- business logic

## Default State

- paper account implemented: false
- simulated order engine implemented: false
- simulated fill engine implemented: false
- paper position logic implemented: false
- PnL logic implemented: false
- strategy integration implemented: false
- risk integration implemented: false
- broker integration implemented: false

## Exit Criteria

- tests pass
- paper_trading stack has contracts/services/api placeholders
- all paper orders rejected by skeleton
- no fill engine exists
- no strategy/risk/broker integration exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_9_PAPER_TRADING_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 9 Paper Trading Skeleton Certification

Status: pending

Checks:
- paper_trading contract exists
- skeleton service exists
- API placeholder exists
- all paper orders rejected by default
- no fill engine implementation
- no PnL implementation
- no strategy integration
- no risk integration
- no broker integration
- tests pass
EOF

echo
echo "Running Phase 9 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_9_PAPER_TRADING_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 9 Paper Trading Skeleton Certification

Status: PASS

Checks:
- paper_trading contract exists
- skeleton service exists
- API placeholder exists
- all paper orders rejected by default
- no fill engine implementation
- no PnL implementation
- no strategy integration
- no risk integration
- no broker integration
- tests pass

Result:
- Phase 9 paper trading skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 9 COMPLETE"
echo "========================================="
echo "PASS: Paper Trading skeleton created and certified."
