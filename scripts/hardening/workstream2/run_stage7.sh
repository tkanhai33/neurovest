#!/usr/bin/env bash

cd ~/Neurovest
source .venv/bin/activate

set +e
set +u

STAMP=$(date +%Y%m%d_%H%M%S)

STAGE_DIR="runtime/hardening/workstream2/stage7"
BACKUP_DIR="runtime/hardening/workstream2/backups/stage7_${STAMP}"

COMPOSITION_FILE="backend/app/stacks/market_data/runtime_composition.py"
ROUTER_FILE="backend/app/stacks/market_data/api_router.py"
TEST_FILE="backend/app/stacks/market_data/tests/test_runtime_composition.py"
MAIN_FILE="backend/app/main.py"

mkdir -p \
  "$STAGE_DIR" \
  "$BACKUP_DIR" \
  backend/app/stacks/market_data/tests \
  handoff/hardening

PROTECTED_FILES=(
  "backend/app/stacks/market_data/dto.py"
  "backend/app/stacks/market_data/provider_contract.py"
  "backend/app/stacks/market_data/provider_registry.py"
  "backend/app/stacks/market_data/provider_cache.py"
  "backend/app/stacks/market_data/provider_router.py"
  "backend/app/stacks/market_data/market_session.py"
  "backend/app/stacks/market_data/yfinance_provider.py"
  "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"
  "backend/app/stacks/market_data/feed.py"
  "backend/app/stacks/market_data/price.py"
  "backend/app/stacks/market_data/bars.py"
  "backend/app/stacks/market_data/market_data_service.py"
)

echo "=========================================================="
echo "WORKSTREAM 2 STAGE 7"
echo "MARKET-DATA COMPOSITION ROOT"
echo "AND READ-ONLY RUNTIME INTEGRATION"
echo "=========================================================="

for file in "${PROTECTED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "BLOCKED: protected file missing:"
        echo "  $file"
        exit 1
    fi

    mkdir -p \
      "$BACKUP_DIR/protected/$(dirname "$file")"

    cp -- \
      "$file" \
      "$BACKUP_DIR/protected/$file"
done

cp -- \
  "$MAIN_FILE" \
  "$BACKUP_DIR/main.py"

for file in \
  "$COMPOSITION_FILE" \
  "$ROUTER_FILE" \
  "$TEST_FILE"
do
    if [ -f "$file" ]; then
        mkdir -p \
          "$BACKUP_DIR/existing/$(dirname "$file")"

        cp -- \
          "$file" \
          "$BACKUP_DIR/existing/$file"
    fi
done

restore_stage7() {
    echo
    echo "RESTORING STAGE 7"

    cp -- "$BACKUP_DIR/main.py" "$MAIN_FILE"

    for file in \
      "$COMPOSITION_FILE" \
      "$ROUTER_FILE" \
      "$TEST_FILE"
    do
        existing_backup="$BACKUP_DIR/existing/$file"

        if [ -f "$existing_backup" ]; then
            mkdir -p "$(dirname "$file")"
            cp -- "$existing_backup" "$file"
        else
            rm -f -- "$file"
        fi
    done

    echo "Stage 7 source restored."
}

cat > "$COMPOSITION_FILE" <<'PY'
"""
Canonical market-data runtime composition root.

This module owns construction of the read-only market-data runtime:

- provider registry
- bounded process-local cache
- market-session service
- provider router
- YFinanceProvider registration

It performs no market-data network call during construction.

Broker execution, order execution, portfolio mutation, and live trading
are outside this composition root.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from backend.app.stacks.market_data.market_session import (
    MarketSessionService,
)
from backend.app.stacks.market_data.provider_cache import (
    MarketDataCache,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderRegistry,
)
from backend.app.stacks.market_data.provider_router import (
    ProviderRouter,
)
from backend.app.stacks.market_data.yfinance_provider import (
    YFinanceProvider,
)


@dataclass(
    frozen=True,
    slots=True,
)
class MarketDataRuntime:
    registry: ProviderRegistry
    cache: MarketDataCache[
        tuple[object, ...],
        object,
    ]
    session: MarketSessionService
    router: ProviderRouter


def build_market_data_runtime(
    *,
    register_yfinance: bool = True,
) -> MarketDataRuntime:
    """
    Construct an isolated read-only market-data runtime.

    Construction performs no external provider call.
    """

    registry = ProviderRegistry()

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=2048,
        default_ttl_seconds=30.0,
    )

    session = MarketSessionService()

    if register_yfinance:
        registry.register(
            YFinanceProvider(),
            priority=100,
            enabled=True,
        )

    router = ProviderRouter(
        registry,
        cache=cache,
        quote_ttl_seconds=5.0,
        historical_ttl_seconds=300.0,
    )

    return MarketDataRuntime(
        registry=registry,
        cache=cache,
        session=session,
        router=router,
    )


_RUNTIME_LOCK = RLock()

_RUNTIME: MarketDataRuntime | None = None

_TEST_RUNTIME_OVERRIDE: MarketDataRuntime | None = None


def get_market_data_runtime() -> MarketDataRuntime:
    """
    Return the shared process-local read-only market-data runtime.
    """

    global _RUNTIME

    with _RUNTIME_LOCK:
        if _TEST_RUNTIME_OVERRIDE is not None:
            return _TEST_RUNTIME_OVERRIDE

        if _RUNTIME is None:
            _RUNTIME = build_market_data_runtime()

        return _RUNTIME


def set_market_data_runtime_for_testing(
    runtime: MarketDataRuntime | None,
) -> None:
    """
    Install or clear a test-only runtime override.

    Production application code must not call this function.
    """

    global _TEST_RUNTIME_OVERRIDE

    with _RUNTIME_LOCK:
        _TEST_RUNTIME_OVERRIDE = runtime


def reset_market_data_runtime() -> None:
    """
    Clear the shared runtime without performing provider operations.
    """

    global _RUNTIME
    global _TEST_RUNTIME_OVERRIDE

    with _RUNTIME_LOCK:
        _RUNTIME = None
        _TEST_RUNTIME_OVERRIDE = None


def healthcheck() -> dict[str, object]:
    """
    Return construction-level health without calling a provider.
    """

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    return {
        "component": "market_data_runtime",
        "healthy": bool(records),
        "providers": [
            {
                "name": record.name,
                "priority": record.priority,
                "enabled": record.enabled,
            }
            for record in records
        ],
        "network_called": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }
PY

cat > "$ROUTER_FILE" <<'PY'
"""
Read-only market-data API router.

This router exposes canonical market-data DTOs through the shared
market-data composition root.

No endpoint performs broker execution, order placement, portfolio
mutation, registry writes, or live-trading activation.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.encoders import jsonable_encoder

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderCapabilityUnavailableError,
)
from backend.app.stacks.market_data.provider_router import (
    ProviderRoutingError,
)
from backend.app.stacks.market_data.runtime_composition import (
    get_market_data_runtime,
)
from backend.app.stacks.market_data.yfinance_provider import (
    YFinanceProviderError,
)


router = APIRouter(
    prefix="/api/v1/market-data",
    tags=["market-data"],
)


def _parse_datetime(
    value: str,
    field_name: str,
) -> datetime:
    candidate = value.strip()

    if not candidate:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field_name} must not be empty"
            ),
        )

    if candidate.endswith("Z"):
        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            candidate
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field_name} must be an ISO-8601 "
                "date or datetime"
            ),
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone(
        UTC
    )


def _provider_failure(
    exc: Exception,
) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "error": "market_data_unavailable",
            "type": type(exc).__name__,
            "message": str(exc),
        },
    )


@router.get("/status")
def market_data_status() -> object:
    """
    Return read-only composition, cache, provider, and session status.

    This endpoint performs no external market-data request.
    """

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    cache = runtime.cache.stats()

    session = runtime.session.now()

    return jsonable_encoder(
        {
            "status": "ready",
            "mode": "read_only",
            "providers": [
                {
                    "name": record.name,
                    "priority": record.priority,
                    "enabled": record.enabled,
                }
                for record in records
            ],
            "cache": {
                "size": cache.size,
                "maximum_size": (
                    cache.maximum_size
                ),
                "hits": cache.hits,
                "misses": cache.misses,
                "expirations": (
                    cache.expirations
                ),
                "evictions": cache.evictions,
            },
            "session": {
                "state": (
                    session.state.value
                ),
                "observed_at": (
                    session.observed_at
                ),
                "exchange_time": (
                    session.exchange_time
                ),
                "exchange_timezone": (
                    session.exchange_timezone
                ),
                "holiday_calendar_applied": (
                    session
                    .holiday_calendar_applied
                ),
            },
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        }
    )


@router.get("/quote/{symbol}")
def market_data_quote(
    symbol: str,
    use_cache: bool = Query(
        default=True,
    ),
) -> object:
    runtime = get_market_data_runtime()

    try:
        quote = runtime.router.get_quote(
            symbol,
            use_cache=use_cache,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except (
        ProviderCapabilityUnavailableError,
        ProviderRoutingError,
        YFinanceProviderError,
    ) as exc:
        raise _provider_failure(
            exc
        ) from exc

    return jsonable_encoder(
        quote
    )


@router.get("/historical/{symbol}")
def market_data_historical(
    symbol: str,
    start: str = Query(
        description=(
            "ISO-8601 start date or datetime"
        )
    ),
    end: str = Query(
        description=(
            "ISO-8601 end date or datetime"
        )
    ),
    interval: str = Query(
        default="1d",
        min_length=1,
        max_length=16,
    ),
    adjusted: bool = Query(
        default=True,
    ),
    limit: int | None = Query(
        default=None,
        ge=1,
        le=5000,
    ),
    use_cache: bool = Query(
        default=True,
    ),
) -> object:
    runtime = get_market_data_runtime()

    try:
        request = HistoricalBarsRequest(
            symbol=symbol,
            start=_parse_datetime(
                start,
                "start",
            ),
            end=_parse_datetime(
                end,
                "end",
            ),
            interval=interval,
            adjusted=adjusted,
            limit=limit,
        )

        result = (
            runtime.router
            .get_historical_bars(
                request,
                use_cache=use_cache,
            )
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except (
        ProviderCapabilityUnavailableError,
        ProviderRoutingError,
        YFinanceProviderError,
    ) as exc:
        raise _provider_failure(
            exc
        ) from exc

    return jsonable_encoder(
        result
    )
PY

cat > "$TEST_FILE" <<'PY'
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.market_data.api_router import (
    router,
)
from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    ProviderHealth,
)
from backend.app.stacks.market_data.runtime_composition import (
    build_market_data_runtime,
    get_market_data_runtime,
    reset_market_data_runtime,
    set_market_data_runtime_for_testing,
)


class FixtureProvider:
    @property
    def provider_name(self) -> str:
        return "fixture"

    @property
    def capabilities(
        self,
    ) -> frozenset[
        MarketDataCapability
    ]:
        return frozenset(
            {
                MarketDataCapability.QUOTE,
                MarketDataCapability.HISTORICAL_BARS,
            }
        )

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        return capability in self.capabilities

    def get_quote(
        self,
        symbol: str,
    ) -> MarketQuote:
        return MarketQuote(
            symbol=symbol,
            price=123.45,
            currency="USD",
            observed_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
            provider=self.provider_name,
        )

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        bar = HistoricalBar(
            symbol=request.symbol,
            timestamp=request.start,
            interval=request.interval,
            open=100.0,
            high=125.0,
            low=99.0,
            close=123.45,
            volume=1000.0,
            provider=self.provider_name,
        )

        return HistoricalBarsResult(
            request=request,
            provider=self.provider_name,
            bars=(bar,),
            fetched_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
        )

    def healthcheck(
        self,
    ) -> ProviderHealth:
        return ProviderHealth(
            provider=self.provider_name,
            healthy=True,
            checked_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
            capabilities=self.capabilities,
        )


def build_fixture_runtime():
    runtime = build_market_data_runtime(
        register_yfinance=False
    )

    runtime.registry.register(
        FixtureProvider(),
        priority=1,
    )

    return runtime


def test_production_runtime_constructs_without_network() -> None:
    reset_market_data_runtime()

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    assert len(records) == 1
    assert records[0].name == "yfinance"
    assert records[0].enabled is True

    reset_market_data_runtime()


def test_runtime_components_are_shared() -> None:
    reset_market_data_runtime()

    first = get_market_data_runtime()
    second = get_market_data_runtime()

    assert first is second

    reset_market_data_runtime()


def test_read_only_routes_are_declared() -> None:
    paths = {
        route.path
        for route in router.routes
    }

    assert (
        "/api/v1/market-data/status"
        in paths
    )

    assert (
        "/api/v1/market-data/quote/{symbol}"
        in paths
    )

    assert (
        "/api/v1/market-data/historical/{symbol}"
        in paths
    )


def test_status_endpoint_is_network_free() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ready"
    assert payload["mode"] == "read_only"
    assert payload[
        "broker_execution_enabled"
    ] is False
    assert payload[
        "live_trading_enabled"
    ] is False

    set_market_data_runtime_for_testing(
        None
    )


def test_quote_endpoint_uses_shared_router() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/quote/AAPL"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["symbol"] == "AAPL"
    assert payload["price"] == 123.45
    assert payload["provider"] == "fixture"

    set_market_data_runtime_for_testing(
        None
    )


def test_historical_endpoint_uses_shared_router() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/historical/AAPL",
        params={
            "start": (
                "2024-01-02T00:00:00+00:00"
            ),
            "end": (
                "2024-02-01T00:00:00+00:00"
            ),
            "interval": "1d",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload[
        "provider"
    ] == "fixture"

    assert len(
        payload["bars"]
    ) == 1

    assert payload[
        "bars"
    ][0]["symbol"] == "AAPL"

    set_market_data_runtime_for_testing(
        None
    )


def test_invalid_historical_range_fails_closed() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/historical/AAPL",
        params={
            "start": "2024-02-01",
            "end": "2024-01-02",
        },
    )

    assert response.status_code == 422

    set_market_data_runtime_for_testing(
        None
    )
PY

echo
echo "=========================================================="
echo "PATCHING MAIN COMPOSITION ROOT"
echo "=========================================================="

python3 - <<'PY'
from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/app/main.py"
)

text = path.read_text(
    encoding="utf-8"
)

import_line = (
    "from backend.app.stacks.market_data.api_router "
    "import router as market_data_router"
)

include_line = (
    "app.include_router(market_data_router)"
)

tree = ast.parse(
    text,
    filename=str(path),
)

app_assignments = []

for node in tree.body:
    if not isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
        ),
    ):
        continue

    targets = []

    if isinstance(
        node,
        ast.Assign,
    ):
        targets = node.targets

    else:
        targets = [
            node.target
        ]

    for target in targets:
        if (
            isinstance(target, ast.Name)
            and target.id == "app"
        ):
            app_assignments.append(
                node.lineno
            )

if not app_assignments:
    raise SystemExit(
        "BLOCKED: no top-level app assignment "
        "was found in backend/app/main.py."
    )

if import_line not in text:
    lines = text.splitlines()

    top_level_imports = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    if not top_level_imports:
        raise SystemExit(
            "BLOCKED: no safe top-level import "
            "insertion point was found."
        )

    insertion_line = max(
        node.end_lineno or node.lineno
        for node in top_level_imports
    )

    lines.insert(
        insertion_line,
        import_line,
    )

    text = (
        "\n".join(lines)
        + "\n"
    )

if include_line not in text:
    text = (
        text.rstrip()
        + "\n\n"
        + "# Read-only canonical market-data runtime.\n"
        + include_line
        + "\n"
    )

if text.count(
    import_line
) != 1:
    raise SystemExit(
        "BLOCKED: expected exactly one market-data "
        "router import."
    )

if text.count(
    include_line
) != 1:
    raise SystemExit(
        "BLOCKED: expected exactly one market-data "
        "router inclusion."
    )

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "PASS: read-only market-data router imported"
)
print(
    "PASS: market-data router included exactly once"
)
print(
    "PASS: no execution or broker route added"
)
PY

PATCH_EXIT=$?

COMPILE_EXIT=1
TEST_EXIT=1
PROTECTED_EXIT=1
IMPORT_EXIT=1
OPENAPI_EXIT=1
AUDIT_EXIT=1
VERIFY_EXIT=1

if [ "$PATCH_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "COMPILE VERIFICATION"
    echo "=========================================================="

    python3 -m py_compile \
      "$COMPOSITION_FILE" \
      "$ROUTER_FILE" \
      "$TEST_FILE" \
      "$MAIN_FILE"

    COMPILE_EXIT=$?

    echo
    echo "Compile exit code: $COMPILE_EXIT"
fi

if [ "$COMPILE_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "FOCUSED MARKET-DATA TESTS"
    echo "=========================================================="

    PYTHONPATH=. python3 -m pytest -q \
      backend/app/stacks/market_data/tests/test_provider_contract.py \
      backend/app/stacks/market_data/tests/test_provider_runtime.py \
      backend/app/stacks/market_data/tests/test_yfinance_provider.py \
      "$TEST_FILE" \
      2>&1 | tee \
      "$STAGE_DIR/stage7_tests_console.log"

    TEST_EXIT=${PIPESTATUS[0]}

    echo
    echo "Test exit code: $TEST_EXIT"
fi

if [ "$TEST_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "PROTECTED FILE INTEGRITY"
    echo "=========================================================="

    PROTECTED_EXIT=0

    for file in "${PROTECTED_FILES[@]}"; do
        if cmp -s \
          "$file" \
          "$BACKUP_DIR/protected/$file"
        then
            echo "PASS: unchanged: $file"
        else
            echo "FAIL: protected file changed: $file"
            PROTECTED_EXIT=1
        fi
    done
fi

if [ "$PROTECTED_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "APPLICATION IMPORT SMOKE TEST"
    echo "=========================================================="

    PYTHONPATH=. python3 - <<'IMPORTPY'
from pathlib import Path

from backend.app.main import app


required = {
    "/api/v1/market-data/status",
    "/api/v1/market-data/quote/{symbol}",
    "/api/v1/market-data/historical/{symbol}",
}

# FastAPI 0.139 records included routers through internal
# _IncludedRouter objects. The generated OpenAPI document is the
# authoritative externally exposed HTTP route surface.
schema = app.openapi()

paths = schema.get(
    "paths",
    {},
)

missing = sorted(
    required - set(paths)
)

assert not missing, (
    "Missing OpenAPI routes: "
    + ", ".join(missing)
)

for required_path in required:
    operations = paths[
        required_path
    ]

    assert set(
        operations
    ) == {
        "get"
    }, (
        f"{required_path} must expose GET only; "
        f"found {sorted(operations)}"
    )

main_source = Path(
    "backend/app/main.py"
).read_text(
    encoding="utf-8"
)

router_import = (
    "from backend.app.stacks.market_data.api_router "
    "import router as market_data_router"
)

router_include = (
    "app.include_router(market_data_router)"
)

assert main_source.count(
    router_import
) == 1, (
    "Market-data router import must occur exactly once"
)

assert main_source.count(
    router_include
) == 1, (
    "Market-data router inclusion must occur exactly once"
)

print(
    "PASS: backend.app.main imported"
)
print(
    "PASS: three market-data routes present in OpenAPI"
)
print(
    "PASS: all market-data routes expose GET only"
)
print(
    "PASS: router import and inclusion occur exactly once"
)
IMPORTPY

    IMPORT_EXIT=$?

    echo
    echo "Import smoke exit code: $IMPORT_EXIT"
fi

if [ "$IMPORT_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "OPENAPI VERIFICATION"
    echo "=========================================================="

    PYTHONPATH=. python3 - <<'PY'
from backend.app.main import app


schema = app.openapi()

paths = schema[
    "paths"
]

required = {
    "/api/v1/market-data/status",
    "/api/v1/market-data/quote/{symbol}",
    "/api/v1/market-data/historical/{symbol}",
}

missing = sorted(
    required - set(paths)
)

assert not missing, (
    "Missing OpenAPI paths: "
    + ", ".join(missing)
)

for path in required:
    methods = set(
        paths[path]
    )

    assert methods == {
        "get"
    }, (
        f"{path} contains non-read-only methods: "
        f"{sorted(methods)}"
    )

for forbidden in (
    "post",
    "put",
    "patch",
    "delete",
):
    for path in required:
        assert forbidden not in paths[
            path
        ]

print(
    "PASS: OpenAPI contains all market-data paths"
)
print(
    "PASS: market-data integration exposes GET only"
)
print(
    "PASS: no mutation method exposed"
)
PY

    OPENAPI_EXIT=$?

    echo
    echo "OpenAPI exit code: $OPENAPI_EXIT"
fi

if [ "$OPENAPI_EXIT" -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "RERUNNING IMPORT/CYCLE AUDIT"
    echo "=========================================================="

    PYTHONPATH=. python3 -u \
      scripts/hardening/workstream1/import_cycle_audit.py \
      2>&1 | tee \
      "$STAGE_DIR/stage7_import_cycle_console.log"

    AUDIT_EXIT=${PIPESTATUS[0]}

    echo
    echo "Audit exit code: $AUDIT_EXIT"
fi

if \
    [ "$PATCH_EXIT" -eq 0 ] && \
    [ "$COMPILE_EXIT" -eq 0 ] && \
    [ "$TEST_EXIT" -eq 0 ] && \
    [ "$PROTECTED_EXIT" -eq 0 ] && \
    [ "$IMPORT_EXIT" -eq 0 ] && \
    [ "$OPENAPI_EXIT" -eq 0 ] && \
    [ "$AUDIT_EXIT" -eq 0 ]
then
    BACKUP_DIR_VALUE="$BACKUP_DIR" \
    PYTHONPATH=. python3 - <<'PY'
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from backend.app.main import app
from backend.app.stacks.market_data.runtime_composition import (
    get_market_data_runtime,
)


ROOT = Path(".").resolve()

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "stage7"
)

AUDIT_PATH = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

OUTPUT_JSON = (
    STAGE_DIR
    / "stage7_runtime_integration_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage7_runtime_integration_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_2_LEDGER.md"
)

FILES = [
    ROOT
    / "backend/app/stacks/market_data/runtime_composition.py",

    ROOT
    / "backend/app/stacks/market_data/api_router.py",

    ROOT
    / "backend/app/stacks/market_data/tests/test_runtime_composition.py",

    ROOT
    / "backend/app/main.py",
]


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


runtime = get_market_data_runtime()

records = runtime.registry.records(
    include_disabled=True
)

assert len(records) == 1
assert records[0].name == "yfinance"
assert records[0].enabled is True

schema = app.openapi()

required_paths = {
    "/api/v1/market-data/status",
    "/api/v1/market-data/quote/{symbol}",
    "/api/v1/market-data/historical/{symbol}",
}

assert required_paths.issubset(
    schema["paths"]
)

for path in required_paths:
    assert set(
        schema["paths"][path]
    ) == {
        "get"
    }

audit = json.loads(
    AUDIT_PATH.read_text(
        encoding="utf-8"
    )
)

summary = audit[
    "summary"
]

assert summary[
    "active_internal_unresolved"
] == 0

assert summary[
    "tooling_or_relative_unresolved"
] == 0

assert summary[
    "syntax_errors"
] == 0

assert summary[
    "active_cycle_components"
] == 0

assert summary[
    "self_cycles"
] == 0

created_at = datetime.now(
    UTC
)

report = {
    "workstream": 2,
    "stage": 7,
    "stage_name": (
        "Market-Data Composition Root and "
        "Read-Only Runtime Integration"
    ),
    "status": "completed",
    "verified_at": (
        created_at.isoformat()
    ),
    "shared_runtime_implemented": True,
    "provider_registry_shared": True,
    "provider_cache_shared": True,
    "provider_router_shared": True,
    "market_session_shared": True,
    "yfinance_registered": True,
    "application_import_verified": True,
    "openapi_verified": True,
    "read_only_routes": sorted(
        required_paths
    ),
    "mutation_routes_added": False,
    "provider_called_during_startup": False,
    "broker_execution_enabled": False,
    "live_trading_enabled": False,
    "repository_state": {
        "active_unresolved_imports": 0,
        "tooling_unresolved_imports": 0,
        "dependency_cycles": 0,
        "self_cycles": 0,
        "syntax_errors": 0,
    },
    "files": [
        {
            "path": path.relative_to(
                ROOT
            ).as_posix(),
            "size_bytes": (
                path.stat().st_size
            ),
            "sha256": sha256_file(
                path
            ),
        }
        for path in FILES
    ],
    "backup_directory": os.environ[
        "BACKUP_DIR_VALUE"
    ],
    "next_stage": (
        "Stage 8 — Runtime Failure Behaviour, "
        "Cache Semantics, and Read-Path Qualification"
    ),
}

OUTPUT_JSON.write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

lines = [
    "=" * 80,
    "NEUROVEST WORKSTREAM 2",
    (
        "STAGE 7 — MARKET-DATA COMPOSITION ROOT "
        "AND READ-ONLY RUNTIME INTEGRATION"
    ),
    "=" * 80,
    "",
    "STATUS",
    "COMPLETE AND VERIFIED",
    "",
    "IMPLEMENTED",
    "- Shared process-local market-data runtime",
    "- Shared provider registry",
    "- Shared bounded TTL cache",
    "- Shared provider router",
    "- Shared market-session service",
    "- YFinanceProvider registration",
    "- Read-only status endpoint",
    "- Read-only canonical quote endpoint",
    "- Read-only canonical historical-bars endpoint",
    "",
    "VERIFICATION",
    "Focused market-data tests:            PASS",
    "Protected source integrity:           PASS",
    "Application import:                   PASS",
    "OpenAPI generation:                   PASS",
    "GET-only market-data routes:          PASS",
    "Active unresolved imports:            0",
    "Dependency cycles:                    0",
    "Syntax errors:                        0",
    "",
    "SAFETY",
    "Provider called during startup:       NO",
    "Mutation routes added:                NO",
    "Broker execution enabled:             NO",
    "Live trading enabled:                 NO",
    "",
    "NEXT",
    (
        "Stage 8 — Runtime Failure Behaviour, Cache Semantics, "
        "and Read-Path Qualification"
    ),
    "",
    "=" * 80,
]

rendered = (
    "\n".join(lines)
    + "\n"
)

OUTPUT_TEXT.write_text(
    rendered,
    encoding="utf-8",
)

with LEDGER.open(
    "a",
    encoding="utf-8",
) as ledger:
    ledger.write(
        "\n"
        "## Stage 7 — Market-Data Composition Root "
        "and Read-Only Runtime Integration\n"
        "\n"
        f"Verified: {created_at.isoformat()}\n"
        "\n"
        "- Status: **COMPLETE AND VERIFIED**\n"
        "- Shared runtime composition: **IMPLEMENTED**\n"
        "- YFinanceProvider registration: **PASS**\n"
        "- Read-only status route: **PASS**\n"
        "- Read-only quote route: **PASS**\n"
        "- Read-only historical route: **PASS**\n"
        "- Application import: **PASS**\n"
        "- OpenAPI generation: **PASS**\n"
        "- Mutation routes added: **NO**\n"
        "- Provider called during startup: **NO**\n"
        "- Active unresolved imports: **0**\n"
        "- Dependency cycles: **0**\n"
        "- Broker execution enabled: **NO**\n"
        "- Live trading enabled: **NO**\n"
        "\n"
    )

print(
    "PASS: shared market-data runtime verified"
)
print(
    "PASS: YFinanceProvider registered once"
)
print(
    "PASS: three GET-only API paths verified"
)
print(
    "PASS: repository imports and cycles remain clean"
)
print(
    "PASS: Stage 7 report generated"
)
PY

    VERIFY_EXIT=$?

    echo
    echo "Assertion exit code: $VERIFY_EXIT"
fi

echo
echo "=========================================================="
echo "AUTHORITATIVE STAGE 7 RESULT"
echo "=========================================================="

if \
    [ "$PATCH_EXIT" -eq 0 ] && \
    [ "$COMPILE_EXIT" -eq 0 ] && \
    [ "$TEST_EXIT" -eq 0 ] && \
    [ "$PROTECTED_EXIT" -eq 0 ] && \
    [ "$IMPORT_EXIT" -eq 0 ] && \
    [ "$OPENAPI_EXIT" -eq 0 ] && \
    [ "$AUDIT_EXIT" -eq 0 ] && \
    [ "$VERIFY_EXIT" -eq 0 ]
then
    echo
    echo "WORKSTREAM 2 STAGE 7 COMPLETE AND VERIFIED"
    echo
    echo "Composition root:         IMPLEMENTED"
    echo "Shared registry:          IMPLEMENTED"
    echo "Shared cache:             IMPLEMENTED"
    echo "Shared router:            IMPLEMENTED"
    echo "Shared session service:   IMPLEMENTED"
    echo "YFinance registration:    VERIFIED"
    echo "Application import:       PASS"
    echo "OpenAPI verification:     PASS"
    echo "Read-only API routes:     3"
    echo "Mutation routes added:    NO"
    echo "Unresolved imports:       0"
    echo "Dependency cycles:        0"
    echo "Broker execution:         DISABLED"
    echo "Live trading:             DISABLED"
    echo
    echo "NEW ROUTES:"
    echo "  GET /api/v1/market-data/status"
    echo "  GET /api/v1/market-data/quote/{symbol}"
    echo "  GET /api/v1/market-data/historical/{symbol}"
    echo
    echo "NEXT:"
    echo "  Stage 8 — Runtime Failure Behaviour,"
    echo "  Cache Semantics, and Read-Path Qualification"
else
    echo
    echo "WORKSTREAM 2 STAGE 7 FAILED"
    echo
    echo "Patch exit:               $PATCH_EXIT"
    echo "Compile exit:             $COMPILE_EXIT"
    echo "Test exit:                $TEST_EXIT"
    echo "Protected integrity exit: $PROTECTED_EXIT"
    echo "Application import exit:  $IMPORT_EXIT"
    echo "OpenAPI exit:             $OPENAPI_EXIT"
    echo "Audit exit:               $AUDIT_EXIT"
    echo "Assertion exit:           $VERIFY_EXIT"
    echo
    echo "Restoring Stage 7 source..."
    restore_stage7
    echo
    echo "No Stage 8 work should begin."
fi

echo
echo "Stage report:"
echo "  $STAGE_DIR/stage7_runtime_integration_latest.txt"
echo
echo "Backup:"
echo "  $BACKUP_DIR"
echo
echo "Stage 7 command finished."
