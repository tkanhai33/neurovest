#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(".").resolve()

BACKEND_URL = "http://127.0.0.1:8000"

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "stage9"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "history"
)

OUTPUT_JSON = (
    STAGE_DIR
    / "stage9_live_backend_qualification_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage9_live_backend_qualification_latest.txt"
)

SYMBOL = "AAPL"

HISTORICAL_PARAMS = {
    "start": "2024-01-02",
    "end": "2024-02-01",
    "interval": "1d",
    "limit": 10,
    "use_cache": "true",
}

REQUEST_COUNT = 200
CONCURRENCY = 25

MAX_ERROR_RATE_PERCENT = 0.0
MAX_P95_MS = 1500.0
MAX_P99_MS = 2500.0


def percentile(
    values: list[float],
    value: float,
) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    position = (
        len(ordered) - 1
    ) * value

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    return (
        ordered[lower]
        + (
            ordered[upper]
            - ordered[lower]
        )
        * (
            position
            - lower
        )
    )


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def require_mapping(
    value: Any,
    name: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AssertionError(
            f"{name} must be an object; "
            f"received {type(value).__name__}"
        )

    return value


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    params: dict[str, str] | None = None,
) -> tuple[
    httpx.Response,
    dict[str, Any],
    float,
]:
    started = time.perf_counter()

    response = await client.request(
        method,
        path,
        params=params,
    )

    latency_ms = (
        time.perf_counter()
        - started
    ) * 1000.0

    try:
        payload = response.json()

    except Exception as exc:
        raise AssertionError(
            f"{method} {path} did not return JSON: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    return (
        response,
        require_mapping(
            payload,
            f"{method} {path} response",
        ),
        latency_ms,
    )


async def run() -> dict[str, Any]:
    STAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timeout = httpx.Timeout(
        connect=10.0,
        read=45.0,
        write=10.0,
        pool=10.0,
    )

    limits = httpx.Limits(
        max_connections=CONCURRENCY + 10,
        max_keepalive_connections=CONCURRENCY,
    )

    async with httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=timeout,
        limits=limits,
    ) as client:
        # -------------------------------------------------
        # OpenAPI and route qualification
        # -------------------------------------------------

        openapi_response = await client.get(
            "/openapi.json"
        )

        if openapi_response.status_code != 200:
            raise AssertionError(
                "Backend OpenAPI is unavailable. "
                f"HTTP {openapi_response.status_code}"
            )

        schema = require_mapping(
            openapi_response.json(),
            "OpenAPI document",
        )

        paths = require_mapping(
            schema.get("paths"),
            "OpenAPI paths",
        )

        required_routes = {
            "/api/v1/market-data/status",
            "/api/v1/market-data/quote/{symbol}",
            "/api/v1/market-data/historical/{symbol}",
        }

        missing_routes = sorted(
            required_routes
            - set(paths)
        )

        if missing_routes:
            raise AssertionError(
                "Running backend does not expose the "
                "Stage 7 market-data routes: "
                + ", ".join(missing_routes)
                + ". Restart the backend using the "
                "current repository source."
            )

        for route in required_routes:
            operations = set(
                require_mapping(
                    paths[route],
                    route,
                )
            )

            if operations != {"get"}:
                raise AssertionError(
                    f"{route} must expose GET only; "
                    f"found {sorted(operations)}"
                )

        # -------------------------------------------------
        # Status and observability before live requests
        # -------------------------------------------------

        (
            status_before_response,
            status_before,
            status_before_latency,
        ) = await request_json(
            client,
            "GET",
            "/api/v1/market-data/status",
        )

        if status_before_response.status_code != 200:
            raise AssertionError(
                "Market-data status failed: "
                f"HTTP {status_before_response.status_code}"
            )

        if status_before.get("mode") != "read_only":
            raise AssertionError(
                "Market-data runtime is not read-only"
            )

        if status_before.get(
            "broker_execution_enabled"
        ) is not False:
            raise AssertionError(
                "Broker execution safety flag is not false"
            )

        if status_before.get(
            "live_trading_enabled"
        ) is not False:
            raise AssertionError(
                "Live-trading safety flag is not false"
            )

        providers = status_before.get(
            "providers"
        )

        if not isinstance(providers, list):
            raise AssertionError(
                "Status provider inventory is missing"
            )

        yfinance_records = [
            provider
            for provider in providers
            if isinstance(provider, dict)
            and provider.get("name") == "yfinance"
        ]

        if len(yfinance_records) != 1:
            raise AssertionError(
                "Expected exactly one registered "
                "yfinance provider"
            )

        if yfinance_records[0].get(
            "enabled"
        ) is not True:
            raise AssertionError(
                "Registered yfinance provider is disabled"
            )

        cache_before = require_mapping(
            status_before.get("cache"),
            "status cache before",
        )

        session_before = require_mapping(
            status_before.get("session"),
            "status session",
        )

        # -------------------------------------------------
        # Real live quote
        # -------------------------------------------------

        (
            quote_response,
            quote,
            quote_latency_ms,
        ) = await request_json(
            client,
            "GET",
            f"/api/v1/market-data/quote/{SYMBOL}",
            params={
                "use_cache": "false",
            },
        )

        if quote_response.status_code != 200:
            raise AssertionError(
                "Live quote failed: "
                f"HTTP {quote_response.status_code}: "
                f"{quote}"
            )

        if quote.get("symbol") != SYMBOL:
            raise AssertionError(
                "Live quote symbol mismatch"
            )

        price = quote.get("price")

        if not isinstance(
            price,
            (
                int,
                float,
            ),
        ) or price <= 0:
            raise AssertionError(
                "Live quote price is not positive"
            )

        if quote.get("provider") != "yfinance":
            raise AssertionError(
                "Live quote provider is not yfinance"
            )

        # Warm the shared cache once.
        (
            warm_response,
            warm_quote,
            warm_latency_ms,
        ) = await request_json(
            client,
            "GET",
            f"/api/v1/market-data/quote/{SYMBOL}",
            params={
                "use_cache": "true",
            },
        )

        if warm_response.status_code != 200:
            raise AssertionError(
                "Quote cache warm request failed"
            )

        if warm_quote.get("symbol") != SYMBOL:
            raise AssertionError(
                "Warm quote symbol mismatch"
            )

        # -------------------------------------------------
        # Cached live backend read qualification
        # -------------------------------------------------

        semaphore = asyncio.Semaphore(
            CONCURRENCY
        )

        latencies: list[float] = []
        status_codes: list[int] = []

        async def one_cached_request() -> None:
            async with semaphore:
                started = time.perf_counter()

                response = await client.get(
                    f"/api/v1/market-data/quote/{SYMBOL}",
                    params={
                        "use_cache": "true",
                    },
                )

                latency_ms = (
                    time.perf_counter()
                    - started
                ) * 1000.0

                latencies.append(
                    latency_ms
                )

                status_codes.append(
                    response.status_code
                )

                if response.status_code == 200:
                    payload = response.json()

                    if payload.get("symbol") != SYMBOL:
                        raise AssertionError(
                            "Concurrent quote symbol mismatch"
                        )

        load_started = time.perf_counter()

        await asyncio.gather(
            *[
                one_cached_request()
                for _ in range(
                    REQUEST_COUNT
                )
            ]
        )

        load_duration = (
            time.perf_counter()
            - load_started
        )

        errors = sum(
            status != 200
            for status in status_codes
        )

        error_rate_percent = (
            errors
            / REQUEST_COUNT
        ) * 100.0

        p50_ms = percentile(
            latencies,
            0.50,
        )

        p95_ms = percentile(
            latencies,
            0.95,
        )

        p99_ms = percentile(
            latencies,
            0.99,
        )

        requests_per_second = (
            REQUEST_COUNT
            / load_duration
            if load_duration > 0
            else 0.0
        )

        if (
            error_rate_percent
            > MAX_ERROR_RATE_PERCENT
        ):
            raise AssertionError(
                "Cached read error rate exceeded threshold"
            )

        if p95_ms > MAX_P95_MS:
            raise AssertionError(
                "Cached read p95 exceeded threshold"
            )

        if p99_ms > MAX_P99_MS:
            raise AssertionError(
                "Cached read p99 exceeded threshold"
            )

        # -------------------------------------------------
        # Real live historical endpoint
        # -------------------------------------------------

        (
            historical_response,
            historical,
            historical_latency_ms,
        ) = await request_json(
            client,
            "GET",
            f"/api/v1/market-data/historical/{SYMBOL}",
            params=HISTORICAL_PARAMS,
        )

        if historical_response.status_code != 200:
            raise AssertionError(
                "Live historical request failed: "
                f"HTTP {historical_response.status_code}: "
                f"{historical}"
            )

        if historical.get("provider") != "yfinance":
            raise AssertionError(
                "Historical provider is not yfinance"
            )

        bars = historical.get("bars")

        if not isinstance(
            bars,
            list,
        ) or not bars:
            raise AssertionError(
                "Historical endpoint returned zero bars"
            )

        for bar in bars:
            if not isinstance(bar, dict):
                raise AssertionError(
                    "Historical bar is not an object"
                )

            if bar.get("symbol") != SYMBOL:
                raise AssertionError(
                    "Historical symbol mismatch"
                )

            high = bar.get("high")
            low = bar.get("low")
            volume = bar.get("volume")

            if not isinstance(
                high,
                (
                    int,
                    float,
                ),
            ):
                raise AssertionError(
                    "Historical high is invalid"
                )

            if not isinstance(
                low,
                (
                    int,
                    float,
                ),
            ):
                raise AssertionError(
                    "Historical low is invalid"
                )

            if high < low:
                raise AssertionError(
                    "Historical high is below low"
                )

            if not isinstance(
                volume,
                (
                    int,
                    float,
                ),
            ) or volume < 0:
                raise AssertionError(
                    "Historical volume is invalid"
                )

        # -------------------------------------------------
        # Observability after reads
        # -------------------------------------------------

        (
            status_after_response,
            status_after,
            status_after_latency,
        ) = await request_json(
            client,
            "GET",
            "/api/v1/market-data/status",
        )

        if status_after_response.status_code != 200:
            raise AssertionError(
                "Post-load status request failed"
            )

        cache_after = require_mapping(
            status_after.get("cache"),
            "status cache after",
        )

        before_hits = int(
            cache_before.get(
                "hits",
                0,
            )
        )

        after_hits = int(
            cache_after.get(
                "hits",
                0,
            )
        )

        before_misses = int(
            cache_before.get(
                "misses",
                0,
            )
        )

        after_misses = int(
            cache_after.get(
                "misses",
                0,
            )
        )

        if after_hits < (
            before_hits
            + REQUEST_COUNT
        ):
            raise AssertionError(
                "Cache-hit observability did not increase "
                "by the qualified request count"
            )

        if status_after.get(
            "broker_execution_enabled"
        ) is not False:
            raise AssertionError(
                "Broker execution flag changed"
            )

        if status_after.get(
            "live_trading_enabled"
        ) is not False:
            raise AssertionError(
                "Live trading flag changed"
            )

    return {
        "backend_url": BACKEND_URL,
        "symbol": SYMBOL,
        "openapi": {
            "required_routes_present": True,
            "get_only_routes_verified": True,
            "required_route_count": 3,
        },
        "provider_observability": {
            "registered_provider": "yfinance",
            "registered_once": True,
            "enabled": True,
        },
        "session_observability": session_before,
        "live_quote": {
            "symbol": quote.get("symbol"),
            "price": quote.get("price"),
            "currency": quote.get("currency"),
            "provider": quote.get("provider"),
            "observed_at": quote.get("observed_at"),
            "latency_ms": round(
                quote_latency_ms,
                3,
            ),
            "warm_latency_ms": round(
                warm_latency_ms,
                3,
            ),
        },
        "live_historical": {
            "symbol": SYMBOL,
            "provider": historical.get("provider"),
            "bar_count": len(bars),
            "latency_ms": round(
                historical_latency_ms,
                3,
            ),
        },
        "read_path": {
            "request_count": REQUEST_COUNT,
            "concurrency": CONCURRENCY,
            "errors": errors,
            "error_rate_percent": round(
                error_rate_percent,
                6,
            ),
            "duration_seconds": round(
                load_duration,
                6,
            ),
            "requests_per_second": round(
                requests_per_second,
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
                    p50_ms,
                    3,
                ),
                "p95": round(
                    p95_ms,
                    3,
                ),
                "p99": round(
                    p99_ms,
                    3,
                ),
                "maximum": round(
                    max(latencies),
                    3,
                ),
            },
        },
        "cache_observability": {
            "before": cache_before,
            "after": cache_after,
            "hit_delta": (
                after_hits
                - before_hits
            ),
            "miss_delta": (
                after_misses
                - before_misses
            ),
        },
        "status_latency_ms": {
            "before": round(
                status_before_latency,
                3,
            ),
            "after": round(
                status_after_latency,
                3,
            ),
        },
        "safety": {
            "mode": "read_only",
            "mutation_routes_added": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        },
    }


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    result = asyncio.run(
        run()
    )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 2,
        "stage": 9,
        "stage_name": (
            "Live Backend Endpoint Qualification, "
            "Provider Observability, and Workstream 2 Freeze"
        ),
        "status": "qualified",
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": round(
            (
                completed_at
                - started_at
            ).total_seconds(),
            6,
        ),
        "qualification": result,
        "thresholds": {
            "maximum_error_rate_percent": (
                MAX_ERROR_RATE_PERCENT
            ),
            "maximum_p95_ms": MAX_P95_MS,
            "maximum_p99_ms": MAX_P99_MS,
        },
        "external_network_used": True,
        "actual_backend_used": True,
        "actual_yfinance_provider_used": True,
        "runtime_source_modified": False,
        "mutation_routes_added": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    serialized = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    OUTPUT_JSON.write_text(
        serialized,
        encoding="utf-8",
    )

    history_name = (
        "stage9_live_backend_qualification_"
        + completed_at.strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )
        + ".json"
    )

    (
        HISTORY_DIR
        / history_name
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    read_path = result[
        "read_path"
    ]

    latency = read_path[
        "latency_ms"
    ]

    cache = result[
        "cache_observability"
    ]

    quote = result[
        "live_quote"
    ]

    historical = result[
        "live_historical"
    ]

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 2",
        (
            "STAGE 9 — LIVE BACKEND ENDPOINT QUALIFICATION, "
            "PROVIDER OBSERVABILITY, AND FINAL FREEZE"
        ),
        "=" * 80,
        "",
        "STATUS",
        "QUALIFIED",
        "",
        "LIVE BACKEND",
        f"Backend:                          {BACKEND_URL}",
        "OpenAPI available:                PASS",
        "Three market-data routes:         PASS",
        "GET-only route enforcement:       PASS",
        "",
        "LIVE PROVIDER",
        "Provider registered:              yfinance",
        "Provider registered once:         PASS",
        "Provider enabled:                 PASS",
        (
            "Live quote price:                "
            f"{quote['price']}"
        ),
        (
            "Live quote latency:              "
            f"{quote['latency_ms']} ms"
        ),
        (
            "Historical bars returned:        "
            f"{historical['bar_count']}"
        ),
        (
            "Historical latency:              "
            f"{historical['latency_ms']} ms"
        ),
        "",
        "LIVE READ-PATH QUALIFICATION",
        (
            "Requests:                         "
            f"{read_path['request_count']}"
        ),
        (
            "Concurrency:                      "
            f"{read_path['concurrency']}"
        ),
        (
            "Errors:                           "
            f"{read_path['errors']}"
        ),
        (
            "Error rate:                       "
            f"{read_path['error_rate_percent']}%"
        ),
        (
            "Requests per second:              "
            f"{read_path['requests_per_second']}"
        ),
        (
            "Average latency:                  "
            f"{latency['average']} ms"
        ),
        (
            "p95 latency:                      "
            f"{latency['p95']} ms"
        ),
        (
            "p99 latency:                      "
            f"{latency['p99']} ms"
        ),
        "",
        "OBSERVABILITY",
        (
            "Cache-hit increase:               "
            f"{cache['hit_delta']}"
        ),
        (
            "Cache-miss increase:              "
            f"{cache['miss_delta']}"
        ),
        "Provider inventory visible:         PASS",
        "Session state visible:              PASS",
        "Cache statistics visible:           PASS",
        "",
        "SAFETY",
        "Runtime source modified:            NO",
        "Mutation routes added:              NO",
        "Broker execution enabled:           NO",
        "Live trading enabled:               NO",
        "",
        "NEXT",
        "Freeze Workstream 2 after repository verification.",
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

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except Exception as exc:
        print("=" * 80)
        print("WORKSTREAM 2 STAGE 9 FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print(
            "The running backend may require a restart "
            "to load the current Stage 7 routes."
        )
        print(
            "No runtime source was intentionally modified."
        )
        print(
            "Broker execution remains disabled."
        )
        print(
            "Live trading remains disabled."
        )
        print("=" * 80)

        raise SystemExit(1)
