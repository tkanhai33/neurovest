#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/market_data"

echo "========================================="
echo "PHASE 4 - MARKET DATA SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/market_data_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarketDataProvider(StrEnum):
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"


class ExchangeStatus(StrEnum):
    UNKNOWN = "unknown"
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class SymbolContract:
    symbol: str
    exchange: str
    currency: str


@dataclass(frozen=True)
class QuoteContract:
    symbol: str
    provider: MarketDataProvider
    price: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class CandleContract:
    symbol: str
    provider: MarketDataProvider
    timestamp: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None


@dataclass(frozen=True)
class MarketDataSkeletonStatus:
    stack: str = "market_data"
    phase: str = "phase_4_skeleton"
    yfinance_adapter_implemented: bool = False
    finnhub_adapter_implemented: bool = False
    live_provider_calls_enabled: bool = False
    strategy_logic_implemented: bool = False
    risk_logic_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/market_data_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.market_data.contracts.market_data_contract import (
    MarketDataSkeletonStatus,
)


def get_market_data_skeleton_status() -> MarketDataSkeletonStatus:
    return MarketDataSkeletonStatus()
EOF

cat > "$STACK/api/market_data_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.market_data.services.market_data_service import (
    get_market_data_skeleton_status,
)

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/status")
def market_data_status() -> dict[str, object]:
    status = get_market_data_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "yfinance_adapter_implemented": status.yfinance_adapter_implemented,
        "finnhub_adapter_implemented": status.finnhub_adapter_implemented,
        "live_provider_calls_enabled": status.live_provider_calls_enabled,
        "strategy_logic_implemented": status.strategy_logic_implemented,
        "risk_logic_implemented": status.risk_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Market Data Adapters

Phase 4 skeleton only.

Future providers:
- yfinance
- Finnhub free tier

Forbidden in Phase 4:
- real provider calls
- network requests
- strategy logic
- risk logic
- broker logic
EOF

cat > "$STACK/adapters/yfinance_adapter.py" <<'EOF'
from __future__ import annotations


def yfinance_adapter_placeholder() -> str:
    return "phase_4_skeleton_only_no_provider_calls"
EOF

cat > "$STACK/adapters/finnhub_adapter.py" <<'EOF'
from __future__ import annotations


def finnhub_adapter_placeholder() -> str:
    return "phase_4_skeleton_only_no_provider_calls"
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Market Data Domain

Phase 4 skeleton only.

Allowed:
- symbol contract
- quote contract
- candle contract
- provider enum
- exchange status enum

Forbidden:
- real provider calls
- strategy calculations
- risk calculations
- broker interaction
- portfolio mutation
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Market Data Stack Tests

Phase 4 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# market_data

Phase 4 — Market Data Skeleton.

Owns:
- symbol contracts
- quote contracts
- candle contracts
- provider identity
- exchange status contracts
- future yfinance/Finnhub adapter boundaries

Forbidden in Phase 4:
- real market data provider calls
- network requests
- strategy logic
- risk logic
- broker access
- portfolio mutation
EOF

cat > "$BACKEND/tests/contracts/test_market_data_contract.py" <<'EOF'
from app.stacks.market_data.contracts.market_data_contract import (
    CandleContract,
    ExchangeStatus,
    MarketDataProvider,
    MarketDataSkeletonStatus,
    QuoteContract,
    SymbolContract,
)


def test_symbol_contract_shape() -> None:
    symbol = SymbolContract(symbol="RY.TO", exchange="TSX", currency="CAD")

    assert symbol.symbol == "RY.TO"
    assert symbol.exchange == "TSX"
    assert symbol.currency == "CAD"


def test_quote_contract_shape() -> None:
    quote = QuoteContract(
        symbol="RY.TO",
        provider=MarketDataProvider.YFINANCE,
        price=None,
        currency="CAD",
    )

    assert quote.symbol == "RY.TO"
    assert quote.provider == MarketDataProvider.YFINANCE
    assert quote.price is None
    assert quote.currency == "CAD"


def test_candle_contract_shape() -> None:
    candle = CandleContract(
        symbol="RY.TO",
        provider=MarketDataProvider.YFINANCE,
        timestamp="2026-07-01T00:00:00Z",
    )

    assert candle.symbol == "RY.TO"
    assert candle.provider == MarketDataProvider.YFINANCE
    assert candle.timestamp == "2026-07-01T00:00:00Z"


def test_exchange_status_contract_shape() -> None:
    assert ExchangeStatus.UNKNOWN == "unknown"
    assert ExchangeStatus.OPEN == "open"
    assert ExchangeStatus.CLOSED == "closed"


def test_market_data_skeleton_status_locked() -> None:
    status = MarketDataSkeletonStatus()

    assert status.stack == "market_data"
    assert status.phase == "phase_4_skeleton"
    assert status.yfinance_adapter_implemented is False
    assert status.finnhub_adapter_implemented is False
    assert status.live_provider_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.risk_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_market_data_status.py" <<'EOF'
from app.stacks.market_data.adapters.finnhub_adapter import (
    finnhub_adapter_placeholder,
)
from app.stacks.market_data.adapters.yfinance_adapter import (
    yfinance_adapter_placeholder,
)
from app.stacks.market_data.services.market_data_service import (
    get_market_data_skeleton_status,
)


def test_market_data_status_is_skeleton_only() -> None:
    status = get_market_data_skeleton_status()

    assert status.stack == "market_data"
    assert status.phase == "phase_4_skeleton"
    assert status.live_provider_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.risk_logic_implemented is False
    assert status.business_logic_implemented is False


def test_market_data_provider_placeholders_do_not_call_network() -> None:
    assert yfinance_adapter_placeholder() == "phase_4_skeleton_only_no_provider_calls"
    assert finnhub_adapter_placeholder() == "phase_4_skeleton_only_no_provider_calls"
EOF

cat > "$BACKEND/tests/architecture/test_market_data_phase_4_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "market_data"

FORBIDDEN_TERMS = [
    "import yfinance",
    "import finnhub",
    "requests.get",
    "httpx.get",
    "submit_order",
    "place_order",
    "execute_trade",
    "risk_approved",
    "strategy_score",
]


def test_market_data_phase_4_has_no_provider_or_trading_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden market data implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_4_MARKET_DATA_SKELETON_CONTRACT.md" <<'EOF'
# Phase 4 Market Data Skeleton Contract

## Status

Phase 4 skeleton only.

## Purpose

Create the market data stack shape without implementing real provider calls.

## Allowed

- symbol contract
- quote contract
- candle contract
- provider enum
- exchange status enum
- yfinance placeholder adapter
- Finnhub placeholder adapter
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real yfinance calls
- real Finnhub calls
- network requests
- strategy logic
- risk logic
- broker interaction
- portfolio mutation
- business logic

## Default State

- yfinance adapter implemented: false
- Finnhub adapter implemented: false
- live provider calls enabled: false
- strategy logic implemented: false
- risk logic implemented: false

## Exit Criteria

- tests pass
- market_data stack has contracts/services/api/adapters placeholders
- no real provider implementation exists
- no strategy/risk/broker logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_4_MARKET_DATA_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 4 Market Data Skeleton Certification

Status: pending

Checks:
- market_data contract exists
- skeleton service exists
- API placeholder exists
- yfinance placeholder exists
- Finnhub placeholder exists
- no real provider calls
- no strategy logic
- no risk logic
- no broker logic
- tests pass
EOF

echo
echo "Running Phase 4 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_4_MARKET_DATA_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 4 Market Data Skeleton Certification

Status: PASS

Checks:
- market_data contract exists
- skeleton service exists
- API placeholder exists
- yfinance placeholder exists
- Finnhub placeholder exists
- no real provider calls
- no strategy logic
- no risk logic
- no broker logic
- tests pass

Result:
- Phase 4 market data skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 4 COMPLETE"
echo "========================================="
echo "PASS: Market Data skeleton created and certified."
