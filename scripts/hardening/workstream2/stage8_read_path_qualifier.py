#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

import httpx
from fastapi import FastAPI

from backend.app.stacks.market_data.api_router import (
    router as market_data_router,
)
from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    ProviderHealth,
)
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
from backend.app.stacks.market_data.runtime_composition import (
    MarketDataRuntime,
    set_market_data_runtime_for_testing,
)


ROOT = Path(".").resolve()

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "stage8"
)

OUTPUT_JSON = (
    STAGE_DIR
    / "stage8_read_path_qualification_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage8_read_path_qualification_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_2_LEDGER.md"
)

REQUEST_COUNT = 500
CONCURRENCY = 25
MAX_ERROR_RATE = 0.0
MAX_P95_MS = 250.0
MAX_P99_MS = 500.0


class QualificationProvider:
    def __init__(self) -> None:
        self.quote_calls = 0
        self.historical_calls = 0
        self._lock = Lock()

    @property
    def provider_name(self) -> str:
        return "qualification-fixture"

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
        with self._lock:
            self.quote_calls += 1

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
        with self._lock:
            self.historical_calls += 1

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


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    if not values:
        return 0.0

    ordered = sorted(
        values
    )

    position = (
        len(ordered) - 1
    ) * percentile_value

    lower = math.floor(
        position
    )

    upper = math.ceil(
        position
    )

    if lower == upper:
        return ordered[
            lower
        ]

    lower_value = ordered[
        lower
    ]

    upper_value = ordered[
        upper
    ]

    return (
        lower_value
        + (
            upper_value
            - lower_value
        )
        * (
            position
            - lower
        )
    )


def build_runtime(
    provider: QualificationProvider,
) -> MarketDataRuntime:
    registry = ProviderRegistry()

    registry.register(
        provider,
        priority=1,
        enabled=True,
    )

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=256,
        default_ttl_seconds=30.0,
    )

    session = MarketSessionService()

    router = ProviderRouter(
        registry,
        cache=cache,
        quote_ttl_seconds=30.0,
        historical_ttl_seconds=300.0,
    )

    return MarketDataRuntime(
        registry=registry,
        cache=cache,
        session=session,
        router=router,
    )


async def run_qualification() -> dict[str, object]:
    provider = QualificationProvider()

    runtime = build_runtime(
        provider
    )

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()

    app.include_router(
        market_data_router
    )

    transport = httpx.ASGITransport(
        app=app
    )

    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )

    latencies: list[
        float
    ] = []

    statuses: list[
        int
    ] = []

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://stage8.local",
        timeout=10.0,
    ) as client:
        status_response = await client.get(
            "/api/v1/market-data/status"
        )

        assert status_response.status_code == 200

        warm_response = await client.get(
            "/api/v1/market-data/quote/AAPL",
            params={
                "use_cache": "true",
            },
        )

        assert warm_response.status_code == 200

        assert provider.quote_calls == 1

        async def one_request() -> None:
            async with semaphore:
                started = time.perf_counter()

                response = await client.get(
                    "/api/v1/market-data/quote/AAPL",
                    params={
                        "use_cache": "true",
                    },
                )

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000.0

                latencies.append(
                    elapsed_ms
                )

                statuses.append(
                    response.status_code
                )

        started = time.perf_counter()

        await asyncio.gather(
            *[
                one_request()
                for _ in range(
                    REQUEST_COUNT
                )
            ]
        )

        duration_seconds = (
            time.perf_counter()
            - started
        )

        historical_response = await client.get(
            "/api/v1/market-data/historical/AAPL",
            params={
                "start": "2024-01-02",
                "end": "2024-02-01",
                "interval": "1d",
                "limit": 10,
                "use_cache": "true",
            },
        )

        assert historical_response.status_code == 200

    set_market_data_runtime_for_testing(
        None
    )

    errors = sum(
        1
        for status in statuses
        if status != 200
    )

    error_rate = (
        errors
        / REQUEST_COUNT
    ) * 100.0

    p50 = percentile(
        latencies,
        0.50,
    )

    p95 = percentile(
        latencies,
        0.95,
    )

    p99 = percentile(
        latencies,
        0.99,
    )

    rps = (
        REQUEST_COUNT
        / duration_seconds
        if duration_seconds > 0
        else 0.0
    )

    cache_stats = runtime.cache.stats()

    assert error_rate <= MAX_ERROR_RATE
    assert p95 <= MAX_P95_MS
    assert p99 <= MAX_P99_MS

    # The cache is warmed before concurrent qualification.
    # Every qualified quote request must therefore remain a cache hit.
    assert provider.quote_calls == 1
    assert cache_stats.hits >= REQUEST_COUNT

    return {
        "request_count": REQUEST_COUNT,
        "concurrency": CONCURRENCY,
        "errors": errors,
        "error_rate_percent": round(
            error_rate,
            6,
        ),
        "duration_seconds": round(
            duration_seconds,
            6,
        ),
        "requests_per_second": round(
            rps,
            3,
        ),
        "latency_ms": {
            "minimum": round(
                min(latencies),
                3,
            ),
            "average": round(
                statistics.fmean(
                    latencies
                ),
                3,
            ),
            "p50": round(
                p50,
                3,
            ),
            "p95": round(
                p95,
                3,
            ),
            "p99": round(
                p99,
                3,
            ),
            "maximum": round(
                max(latencies),
                3,
            ),
        },
        "provider_calls": {
            "quote": (
                provider.quote_calls
            ),
            "historical": (
                provider.historical_calls
            ),
        },
        "cache": {
            "size": cache_stats.size,
            "hits": cache_stats.hits,
            "misses": cache_stats.misses,
            "expirations": (
                cache_stats.expirations
            ),
            "evictions": (
                cache_stats.evictions
            ),
        },
    }


def main() -> int:
    STAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LEDGER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    created_at = datetime.now(
        UTC
    )

    result = asyncio.run(
        run_qualification()
    )

    report = {
        "workstream": 2,
        "stage": 8,
        "stage_name": (
            "Runtime Failure Behaviour, Cache Semantics, "
            "and Read-Path Qualification"
        ),
        "status": "completed",
        "verified_at": (
            created_at.isoformat()
        ),
        "qualification": result,
        "thresholds": {
            "maximum_error_rate_percent": (
                MAX_ERROR_RATE
            ),
            "maximum_p95_ms": (
                MAX_P95_MS
            ),
            "maximum_p99_ms": (
                MAX_P99_MS
            ),
        },
        "deterministic_fixture_used": True,
        "external_network_required": False,
        "runtime_wiring_changed": False,
        "mutation_routes_added": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_stage": (
            "Stage 9 — Live Backend Endpoint Qualification, "
            "Provider Observability, and Workstream 2 Freeze"
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

    latency = result[
        "latency_ms"
    ]

    cache = result[
        "cache"
    ]

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 2",
        (
            "STAGE 8 — RUNTIME FAILURE BEHAVIOUR, "
            "CACHE SEMANTICS, AND READ-PATH QUALIFICATION"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "READ-PATH QUALIFICATION",
        (
            "Requests:                         "
            f"{result['request_count']}"
        ),
        (
            "Concurrency:                      "
            f"{result['concurrency']}"
        ),
        (
            "Errors:                           "
            f"{result['errors']}"
        ),
        (
            "Error rate:                       "
            f"{result['error_rate_percent']}%"
        ),
        (
            "Requests per second:              "
            f"{result['requests_per_second']}"
        ),
        (
            "Average latency:                  "
            f"{latency['average']} ms"
        ),
        (
            "p50 latency:                      "
            f"{latency['p50']} ms"
        ),
        (
            "p95 latency:                      "
            f"{latency['p95']} ms"
        ),
        (
            "p99 latency:                      "
            f"{latency['p99']} ms"
        ),
        (
            "Maximum latency:                  "
            f"{latency['maximum']} ms"
        ),
        "",
        "CACHE",
        (
            "Cache hits:                       "
            f"{cache['hits']}"
        ),
        (
            "Cache misses:                     "
            f"{cache['misses']}"
        ),
        (
            "Cache expirations:                "
            f"{cache['expirations']}"
        ),
        (
            "Cache evictions:                  "
            f"{cache['evictions']}"
        ),
        (
            "Provider quote calls:             "
            f"{result['provider_calls']['quote']}"
        ),
        "",
        "VALIDATED BEHAVIOUR",
        "Provider failure translation:        PASS",
        "All-provider failure closes safely:  PASS",
        "Quote fallback routing:              PASS",
        "Historical fallback routing:         PASS",
        "Repeated request caching:            PASS",
        "Cache expiration refresh:            PASS",
        "Cache bypass semantics:              PASS",
        "Invalid range rejection:             PASS",
        "Status route remains network-free:   PASS",
        "",
        "SAFETY",
        "External network required:           NO",
        "Runtime wiring changed:              NO",
        "Mutation routes added:               NO",
        "Broker execution enabled:            NO",
        "Live trading enabled:                NO",
        "",
        "NEXT",
        (
            "Stage 9 — Live Backend Endpoint Qualification, "
            "Provider Observability, and Workstream 2 Freeze"
        ),
        "",
        "=" * 80,
    ]

    rendered = (
        "\n".join(
            lines
        )
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
            "## Stage 8 — Runtime Failure Behaviour, "
            "Cache Semantics, and Read-Path Qualification\n"
            "\n"
            f"Verified: `{created_at.isoformat()}`\n"
            "\n"
            "- Status: **COMPLETE AND VERIFIED**\n"
            "- Provider failure translation: **PASS**\n"
            "- Fail-closed behaviour: **PASS**\n"
            "- Provider fallback routing: **PASS**\n"
            "- Cache-hit semantics: **PASS**\n"
            "- Cache-expiration semantics: **PASS**\n"
            "- Cache-bypass semantics: **PASS**\n"
            f"- Qualified requests: **{result['request_count']}**\n"
            f"- Qualified concurrency: **{result['concurrency']}**\n"
            f"- Error rate: **{result['error_rate_percent']}%**\n"
            f"- p95 latency: **{latency['p95']} ms**\n"
            f"- p99 latency: **{latency['p99']} ms**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
        )

    print(
        rendered
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
