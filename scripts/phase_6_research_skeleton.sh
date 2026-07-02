#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/research"

echo "========================================="
echo "PHASE 6 - RESEARCH SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/research_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ResearchOutputType(StrEnum):
    INDICATOR = "indicator"
    SCREENER = "screener"
    BACKTEST = "backtest"
    NEWS_SUMMARY = "news_summary"
    HISTORICAL_COMPARISON = "historical_comparison"


@dataclass(frozen=True)
class IndicatorRequestContract:
    symbol: str
    indicator_name: str
    period: str | None = None


@dataclass(frozen=True)
class ScreenerRequestContract:
    universe_name: str
    filter_name: str


@dataclass(frozen=True)
class BacktestRequestContract:
    strategy_name: str
    symbol: str
    start_date: str | None = None
    end_date: str | None = None


@dataclass(frozen=True)
class ResearchOutputContract:
    output_type: ResearchOutputType
    symbol: str | None = None
    summary: str | None = None


@dataclass(frozen=True)
class ResearchSkeletonStatus:
    stack: str = "research"
    phase: str = "phase_6_skeleton"
    indicators_implemented: bool = False
    screeners_implemented: bool = False
    backtests_implemented: bool = False
    news_analysis_implemented: bool = False
    market_data_calls_enabled: bool = False
    strategy_logic_implemented: bool = False
    trading_logic_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/research_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.research.contracts.research_contract import (
    ResearchSkeletonStatus,
)


def get_research_skeleton_status() -> ResearchSkeletonStatus:
    return ResearchSkeletonStatus()
EOF

cat > "$STACK/api/research_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.research.services.research_service import (
    get_research_skeleton_status,
)

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/status")
def research_status() -> dict[str, object]:
    status = get_research_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "indicators_implemented": status.indicators_implemented,
        "screeners_implemented": status.screeners_implemented,
        "backtests_implemented": status.backtests_implemented,
        "news_analysis_implemented": status.news_analysis_implemented,
        "market_data_calls_enabled": status.market_data_calls_enabled,
        "strategy_logic_implemented": status.strategy_logic_implemented,
        "trading_logic_implemented": status.trading_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Research Adapters

Phase 6 skeleton only.

Forbidden:
- real market data calls
- real news calls
- scraping
- strategy generation
- trading logic
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Research Domain

Phase 6 skeleton only.

Allowed:
- indicator request contract
- screener request contract
- backtest request contract
- research output contract
- research status contract

Forbidden:
- indicator calculations
- backtest execution
- screener implementation
- news analysis implementation
- strategy generation
- broker interaction
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Research Stack Tests

Phase 6 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# research

Phase 6 — Research Skeleton.

Owns:
- indicator contracts
- screener contracts
- backtest contracts
- news/research output contracts
- future research service boundary

Forbidden in Phase 6:
- indicator calculations
- backtest execution
- market data calls
- news calls
- strategy generation
- trading logic
- broker access
EOF

cat > "$BACKEND/tests/contracts/test_research_contract.py" <<'EOF'
from app.stacks.research.contracts.research_contract import (
    BacktestRequestContract,
    IndicatorRequestContract,
    ResearchOutputContract,
    ResearchOutputType,
    ResearchSkeletonStatus,
    ScreenerRequestContract,
)


def test_indicator_request_contract_shape() -> None:
    request = IndicatorRequestContract(
        symbol="RY.TO",
        indicator_name="rsi",
        period="14",
    )

    assert request.symbol == "RY.TO"
    assert request.indicator_name == "rsi"
    assert request.period == "14"


def test_screener_request_contract_shape() -> None:
    request = ScreenerRequestContract(
        universe_name="tsx_core",
        filter_name="large_cap",
    )

    assert request.universe_name == "tsx_core"
    assert request.filter_name == "large_cap"


def test_backtest_request_contract_shape() -> None:
    request = BacktestRequestContract(
        strategy_name="placeholder_strategy",
        symbol="RY.TO",
        start_date=None,
        end_date=None,
    )

    assert request.strategy_name == "placeholder_strategy"
    assert request.symbol == "RY.TO"


def test_research_output_contract_shape() -> None:
    output = ResearchOutputContract(
        output_type=ResearchOutputType.INDICATOR,
        symbol="RY.TO",
        summary=None,
    )

    assert output.output_type == ResearchOutputType.INDICATOR
    assert output.symbol == "RY.TO"
    assert output.summary is None


def test_research_skeleton_status_locked() -> None:
    status = ResearchSkeletonStatus()

    assert status.stack == "research"
    assert status.phase == "phase_6_skeleton"
    assert status.indicators_implemented is False
    assert status.screeners_implemented is False
    assert status.backtests_implemented is False
    assert status.news_analysis_implemented is False
    assert status.market_data_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.trading_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_research_status.py" <<'EOF'
from app.stacks.research.services.research_service import (
    get_research_skeleton_status,
)


def test_research_status_is_skeleton_only() -> None:
    status = get_research_skeleton_status()

    assert status.stack == "research"
    assert status.phase == "phase_6_skeleton"
    assert status.indicators_implemented is False
    assert status.screeners_implemented is False
    assert status.backtests_implemented is False
    assert status.news_analysis_implemented is False
    assert status.market_data_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.trading_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/architecture/test_research_phase_6_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "research"

FORBIDDEN_TERMS = [
    "import yfinance",
    "import finnhub",
    "requests.get",
    "httpx.get",
    "calculate_rsi",
    "calculate_macd",
    "run_backtest",
    "generate_signal",
    "submit_order",
    "place_order",
    "execute_trade",
]


def test_research_phase_6_has_no_calculation_or_trading_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden research implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_6_RESEARCH_SKELETON_CONTRACT.md" <<'EOF'
# Phase 6 Research Skeleton Contract

## Status

Phase 6 skeleton only.

## Purpose

Create the research stack shape without implementing calculations, screeners, backtests, news analysis, or strategy generation.

## Allowed

- indicator request contract
- screener request contract
- backtest request contract
- research output contract
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- indicator calculations
- screener implementation
- backtest execution
- market data calls
- news calls
- strategy generation
- broker interaction
- trading logic
- business logic

## Default State

- indicators implemented: false
- screeners implemented: false
- backtests implemented: false
- news analysis implemented: false
- market data calls enabled: false
- strategy logic implemented: false
- trading logic implemented: false

## Exit Criteria

- tests pass
- research stack has contracts/services/api placeholders
- no calculations exist
- no provider calls exist
- no strategy/trading logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_6_RESEARCH_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 6 Research Skeleton Certification

Status: pending

Checks:
- research contract exists
- skeleton service exists
- API placeholder exists
- no indicator calculations
- no backtest execution
- no market data calls
- no strategy logic
- no trading logic
- tests pass
EOF

echo
echo "Running Phase 6 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_6_RESEARCH_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 6 Research Skeleton Certification

Status: PASS

Checks:
- research contract exists
- skeleton service exists
- API placeholder exists
- no indicator calculations
- no backtest execution
- no market data calls
- no strategy logic
- no trading logic
- tests pass

Result:
- Phase 6 research skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 6 COMPLETE"
echo "========================================="
echo "PASS: Research skeleton created and certified."
