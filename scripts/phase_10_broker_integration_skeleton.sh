#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/broker_integration"

echo "========================================="
echo "PHASE 10 - BROKER INTEGRATION SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/broker_integration_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BrokerProvider(StrEnum):
    SNAPTRADE = "snaptrade"


class BrokerConnectionStatus(StrEnum):
    NOT_CONFIGURED = "not_configured"
    LOCKED = "locked"
    READ_ONLY_READY = "read_only_ready"


@dataclass(frozen=True)
class BrokerAccountContract:
    broker_account_id: str
    provider: BrokerProvider
    status: BrokerConnectionStatus = BrokerConnectionStatus.LOCKED


@dataclass(frozen=True)
class BrokerPositionContract:
    symbol: str
    quantity: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class BrokerOrderPreviewContract:
    symbol: str
    side: str
    quantity: float | None = None
    preview_only: bool = True


@dataclass(frozen=True)
class BrokerIntegrationSkeletonStatus:
    stack: str = "broker_integration"
    phase: str = "phase_10_skeleton"
    provider: BrokerProvider = BrokerProvider.SNAPTRADE
    broker_auth_implemented: bool = False
    token_storage_implemented: bool = False
    account_sync_implemented: bool = False
    read_only_calls_enabled: bool = False
    order_preview_implemented: bool = False
    order_submission_implemented: bool = False
    live_trading_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/broker_integration_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerIntegrationSkeletonStatus,
    BrokerOrderPreviewContract,
)


def get_broker_integration_skeleton_status() -> BrokerIntegrationSkeletonStatus:
    return BrokerIntegrationSkeletonStatus()


def reject_all_broker_order_previews_in_skeleton(
    preview: BrokerOrderPreviewContract,
) -> BrokerOrderPreviewContract:
    return BrokerOrderPreviewContract(
        symbol=preview.symbol,
        side=preview.side,
        quantity=preview.quantity,
        preview_only=True,
    )
EOF

cat > "$STACK/api/broker_integration_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.broker_integration.services.broker_integration_service import (
    get_broker_integration_skeleton_status,
)

router = APIRouter(prefix="/broker-integration", tags=["broker-integration"])


@router.get("/status")
def broker_integration_status() -> dict[str, object]:
    status = get_broker_integration_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "provider": status.provider,
        "broker_auth_implemented": status.broker_auth_implemented,
        "token_storage_implemented": status.token_storage_implemented,
        "account_sync_implemented": status.account_sync_implemented,
        "read_only_calls_enabled": status.read_only_calls_enabled,
        "order_preview_implemented": status.order_preview_implemented,
        "order_submission_implemented": status.order_submission_implemented,
        "live_trading_implemented": status.live_trading_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Broker Integration Adapters

Phase 10 skeleton only.

Future provider:
- SnapTrade

Forbidden:
- real SnapTrade API calls
- authentication flows
- token storage
- account synchronization
- order preview implementation
- order submission
- live trading
EOF

cat > "$STACK/adapters/snaptrade_adapter.py" <<'EOF'
from __future__ import annotations


def snaptrade_adapter_placeholder() -> str:
    return "phase_10_skeleton_only_no_broker_calls"
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Broker Integration Domain

Phase 10 skeleton only.

Allowed:
- broker provider enum
- broker account contract
- broker position contract
- broker order preview contract
- broker skeleton status

Forbidden:
- real broker authentication
- token persistence
- account sync
- order submission
- live trading
- execution
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Broker Integration Stack Tests

Phase 10 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# broker_integration

Phase 10 — Broker Integration Skeleton.

Owns:
- future broker connection boundary
- future SnapTrade provider boundary
- future account read-only boundary
- future order preview boundary

Forbidden in Phase 10:
- real SnapTrade API calls
- broker authentication
- token persistence
- account sync
- order submission
- live trading
- execution
EOF

cat > "$BACKEND/tests/contracts/test_broker_integration_contract.py" <<'EOF'
from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerAccountContract,
    BrokerConnectionStatus,
    BrokerIntegrationSkeletonStatus,
    BrokerOrderPreviewContract,
    BrokerPositionContract,
    BrokerProvider,
)


def test_broker_account_contract_shape() -> None:
    account = BrokerAccountContract(
        broker_account_id="broker_001",
        provider=BrokerProvider.SNAPTRADE,
    )

    assert account.broker_account_id == "broker_001"
    assert account.provider == BrokerProvider.SNAPTRADE
    assert account.status == BrokerConnectionStatus.LOCKED


def test_broker_position_contract_shape() -> None:
    position = BrokerPositionContract(symbol="RY.TO", currency="CAD")

    assert position.symbol == "RY.TO"
    assert position.quantity is None
    assert position.currency == "CAD"


def test_broker_order_preview_contract_shape() -> None:
    preview = BrokerOrderPreviewContract(
        symbol="RY.TO",
        side="buy",
        quantity=None,
    )

    assert preview.symbol == "RY.TO"
    assert preview.side == "buy"
    assert preview.quantity is None
    assert preview.preview_only is True


def test_broker_integration_skeleton_status_locked() -> None:
    status = BrokerIntegrationSkeletonStatus()

    assert status.stack == "broker_integration"
    assert status.phase == "phase_10_skeleton"
    assert status.provider == BrokerProvider.SNAPTRADE
    assert status.broker_auth_implemented is False
    assert status.token_storage_implemented is False
    assert status.account_sync_implemented is False
    assert status.read_only_calls_enabled is False
    assert status.order_preview_implemented is False
    assert status.order_submission_implemented is False
    assert status.live_trading_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_broker_integration_status.py" <<'EOF'
from app.stacks.broker_integration.adapters.snaptrade_adapter import (
    snaptrade_adapter_placeholder,
)
from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerOrderPreviewContract,
)
from app.stacks.broker_integration.services.broker_integration_service import (
    get_broker_integration_skeleton_status,
    reject_all_broker_order_previews_in_skeleton,
)


def test_broker_integration_status_is_skeleton_only() -> None:
    status = get_broker_integration_skeleton_status()

    assert status.stack == "broker_integration"
    assert status.phase == "phase_10_skeleton"
    assert status.broker_auth_implemented is False
    assert status.token_storage_implemented is False
    assert status.account_sync_implemented is False
    assert status.read_only_calls_enabled is False
    assert status.order_preview_implemented is False
    assert status.order_submission_implemented is False
    assert status.live_trading_implemented is False
    assert status.business_logic_implemented is False


def test_snaptrade_placeholder_does_not_call_broker() -> None:
    assert snaptrade_adapter_placeholder() == "phase_10_skeleton_only_no_broker_calls"


def test_broker_preview_remains_preview_only() -> None:
    preview = BrokerOrderPreviewContract(symbol="RY.TO", side="buy")
    rejected = reject_all_broker_order_previews_in_skeleton(preview)

    assert rejected.preview_only is True
EOF

cat > "$BACKEND/tests/architecture/test_broker_integration_phase_10_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "broker_integration"

FORBIDDEN_TERMS = [
    "import snaptrade",
    "SnapTrade",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "access_token",
    "refresh_token",
    "submit_order",
    "place_order",
    "execute_trade",
    "live_trade",
]


def test_broker_integration_phase_10_has_no_broker_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden broker implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_10_BROKER_INTEGRATION_SKELETON_CONTRACT.md" <<'EOF'
# Phase 10 Broker Integration Skeleton Contract

## Status

Phase 10 skeleton only.

## Purpose

Create the broker integration stack shape without implementing real SnapTrade calls, authentication, token storage, account sync, order preview logic, order submission, live trading, or execution.

## Allowed

- broker provider enum
- broker account contract
- broker position contract
- broker order preview contract
- SnapTrade placeholder adapter
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real SnapTrade API calls
- broker authentication
- token persistence
- account synchronization
- order preview implementation
- order submission
- live trading
- execution
- business logic

## Default State

- broker auth implemented: false
- token storage implemented: false
- account sync implemented: false
- read-only calls enabled: false
- order preview implemented: false
- order submission implemented: false
- live trading implemented: false

## Exit Criteria

- tests pass
- broker_integration stack has contracts/services/api/adapters placeholders
- no real broker calls exist
- no token storage exists
- no order submission exists
- no live trading exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_10_BROKER_INTEGRATION_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 10 Broker Integration Skeleton Certification

Status: pending

Checks:
- broker_integration contract exists
- skeleton service exists
- API placeholder exists
- SnapTrade placeholder exists
- no real broker calls
- no token storage
- no account sync
- no order submission
- no live trading
- tests pass
EOF

echo
echo "Running Phase 10 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_10_BROKER_INTEGRATION_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 10 Broker Integration Skeleton Certification

Status: PASS

Checks:
- broker_integration contract exists
- skeleton service exists
- API placeholder exists
- SnapTrade placeholder exists
- no real broker calls
- no token storage
- no account sync
- no order submission
- no live trading
- tests pass

Result:
- Phase 10 broker integration skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 10 COMPLETE"
echo "========================================="
echo "PASS: Broker Integration skeleton created and certified."
