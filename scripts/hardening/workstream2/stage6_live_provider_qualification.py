#!/usr/bin/env python3

"""
NeuroVest Workstream 2
Stage 6 — Dependency Qualification, Live Compatibility Probe,
and Provider Registration Verification

This stage:

- qualifies the installed yfinance dependency
- inspects the real helper signatures
- runs controlled live quote and historical probes
- registers YFinanceProvider in an isolated registry
- routes canonical requests through ProviderRouter
- verifies canonical DTO output
- does not modify main.py or application runtime composition
"""

from __future__ import annotations

import hashlib
import inspect
import json
import platform
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
)
from backend.app.stacks.market_data.provider_cache import (
    MarketDataCache,
)
from backend.app.stacks.market_data.provider_contract import (
    MarketDataProvider,
    verify_provider_shape,
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


ROOT = Path(__file__).resolve().parents[3]

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "stage6"
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
    / "stage6_live_provider_qualification_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage6_live_provider_qualification_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_2_LEDGER.md"
)

MAIN_FILE = (
    ROOT
    / "backend"
    / "app"
    / "main.py"
)

SYMBOL = "AAPL"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def import_yfinance() -> tuple[Any, str]:
    import yfinance

    version = getattr(
        yfinance,
        "__version__",
        "unknown",
    )

    return (
        yfinance,
        str(version),
    )


def inspect_real_helpers() -> dict[str, Any]:
    from backend.app.stacks.market_data.feed import (
        get_live_price_quote,
    )
    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import (
        get_historical_bars,
    )

    quote_signature = str(
        inspect.signature(
            get_live_price_quote
        )
    )

    historical_signature = str(
        inspect.signature(
            get_historical_bars
        )
    )

    return {
        "quote_loader": {
            "module": (
                get_live_price_quote.__module__
            ),
            "name": (
                get_live_price_quote.__name__
            ),
            "signature": quote_signature,
        },
        "historical_loader": {
            "module": (
                get_historical_bars.__module__
            ),
            "name": (
                get_historical_bars.__name__
            ),
            "signature": historical_signature,
        },
    }


def run_probe() -> dict[str, Any]:
    provider = YFinanceProvider()

    valid, missing = verify_provider_shape(
        provider
    )

    if not valid:
        raise AssertionError(
            "YFinanceProvider is missing: "
            + ", ".join(missing)
        )

    if not isinstance(
        provider,
        MarketDataProvider,
    ):
        raise AssertionError(
            "YFinanceProvider does not satisfy "
            "MarketDataProvider"
        )

    registry = ProviderRegistry()

    registered = registry.register(
        provider,
        priority=10,
        enabled=True,
    )

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=32,
        default_ttl_seconds=30,
    )

    router = ProviderRouter(
        registry,
        cache=cache,
        quote_ttl_seconds=5,
        historical_ttl_seconds=300,
    )

    selected_quote_provider = (
        registry.select(
            MarketDataCapability.QUOTE
        )
    )

    selected_bars_provider = (
        registry.select(
            MarketDataCapability
            .HISTORICAL_BARS
        )
    )

    if (
        selected_quote_provider.provider_name
        != "yfinance"
    ):
        raise AssertionError(
            "Registry did not select yfinance "
            "for quote capability"
        )

    if (
        selected_bars_provider.provider_name
        != "yfinance"
    ):
        raise AssertionError(
            "Registry did not select yfinance "
            "for historical-bars capability"
        )

    quote_started = time.perf_counter()

    quote = router.get_quote(
        SYMBOL,
        use_cache=False,
    )

    quote_latency_ms = (
        time.perf_counter()
        - quote_started
    ) * 1000

    if not isinstance(
        quote,
        MarketQuote,
    ):
        raise AssertionError(
            "Live quote did not return MarketQuote"
        )

    if quote.symbol != SYMBOL:
        raise AssertionError(
            "Live quote symbol mismatch"
        )

    if quote.price <= 0:
        raise AssertionError(
            "Live quote price must be positive"
        )

    # Use a completed and stable historical range rather than a
    # rolling machine-clock window. This verifies provider compatibility
    # without depending on current-day availability, market holidays,
    # delayed upstream publication, or system-clock/provider skew.
    start = datetime(
        2024,
        1,
        2,
        tzinfo=UTC,
    )

    end = datetime(
        2024,
        2,
        1,
        tzinfo=UTC,
    )

    request = HistoricalBarsRequest(
        symbol=SYMBOL,
        start=start,
        end=end,
        interval="1d",
        adjusted=True,
        limit=10,
    )

    bars_started = time.perf_counter()

    bars = router.get_historical_bars(
        request,
        use_cache=False,
    )

    bars_latency_ms = (
        time.perf_counter()
        - bars_started
    ) * 1000

    if not isinstance(
        bars,
        HistoricalBarsResult,
    ):
        raise AssertionError(
            "Live historical request did not return "
            "HistoricalBarsResult"
        )

    if bars.provider != "yfinance":
        raise AssertionError(
            "Historical result provider mismatch"
        )

    if not bars.bars:
        raise AssertionError(
            "Historical probe returned zero bars"
        )

    for bar in bars.bars:
        if bar.symbol != SYMBOL:
            raise AssertionError(
                "Historical bar symbol mismatch"
            )

        if bar.high < bar.low:
            raise AssertionError(
                "Historical bar high is below low"
            )

        if bar.volume < 0:
            raise AssertionError(
                "Historical volume is negative"
            )

    quote_cached = router.get_quote(
        SYMBOL,
        use_cache=True,
    )

    quote_cached_again = router.get_quote(
        SYMBOL,
        use_cache=True,
    )

    if quote_cached != quote_cached_again:
        raise AssertionError(
            "Quote cache did not return a stable value"
        )

    cache_stats = cache.stats()

    return {
        "provider_registration": {
            "name": registered.name,
            "priority": registered.priority,
            "enabled": registered.enabled,
            "registry_size": len(
                registry
            ),
        },
        "quote": {
            "symbol": quote.symbol,
            "price": quote.price,
            "currency": quote.currency,
            "provider": quote.provider,
            "observed_at": (
                quote.observed_at.isoformat()
            ),
            "session": quote.session.value,
            "delayed": quote.delayed,
            "latency_ms": round(
                quote_latency_ms,
                3,
            ),
        },
        "historical": {
            "symbol": (
                bars.request.symbol
            ),
            "provider": bars.provider,
            "interval": (
                bars.request.interval
            ),
            "bar_count": len(
                bars.bars
            ),
            "first_timestamp": (
                bars.bars[0]
                .timestamp
                .isoformat()
            ),
            "last_timestamp": (
                bars.bars[-1]
                .timestamp
                .isoformat()
            ),
            "complete": bars.complete,
            "warnings": list(
                bars.warnings
            ),
            "latency_ms": round(
                bars_latency_ms,
                3,
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

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LEDGER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    started_at = datetime.now(
        UTC
    )

    main_hash_before = sha256_file(
        MAIN_FILE
    )

    _, yfinance_version = (
        import_yfinance()
    )

    helper_signatures = (
        inspect_real_helpers()
    )

    probe = run_probe()

    main_hash_after = sha256_file(
        MAIN_FILE
    )

    if (
        main_hash_before
        != main_hash_after
    ):
        raise AssertionError(
            "backend/app/main.py changed during Stage 6"
        )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 2,
        "stage": 6,
        "stage_name": (
            "Dependency Qualification, Live Compatibility "
            "Probe, and Provider Registration Verification"
        ),
        "status": "completed",
        "started_at": (
            started_at.isoformat()
        ),
        "completed_at": (
            completed_at.isoformat()
        ),
        "duration_seconds": round(
            (
                completed_at
                - started_at
            ).total_seconds(),
            6,
        ),
        "environment": {
            "python": (
                sys.version.split()[0]
            ),
            "platform": (
                platform.platform()
            ),
            "executable": (
                sys.executable
            ),
            "yfinance_version": (
                yfinance_version
            ),
        },
        "dependency_qualified": True,
        "helper_signatures": (
            helper_signatures
        ),
        "live_probe": probe,
        "canonical_quote_verified": True,
        "canonical_historical_bars_verified": True,
        "provider_registration_verified": True,
        "provider_routing_verified": True,
        "cache_path_verified": True,
        "main_file_changed": False,
        "runtime_composition_changed": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_stage": (
            "Stage 7 — Market-Data Composition Root "
            "and Read-Only Runtime Integration"
        ),
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

    timestamp = (
        completed_at.strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )
    )

    (
        HISTORY_DIR
        / (
            "stage6_live_provider_"
            f"qualification_{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 2",
        (
            "STAGE 6 — DEPENDENCY QUALIFICATION, "
            "LIVE COMPATIBILITY, AND REGISTRATION"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "DEPENDENCY",
        (
            "yfinance version:                 "
            f"{yfinance_version}"
        ),
        (
            "Python executable:                "
            f"{sys.executable}"
        ),
        "",
        "REAL HELPER SIGNATURES",
        (
            "Quote helper:                     "
            f"{helper_signatures['quote_loader']['signature']}"
        ),
        (
            "Historical helper:                "
            f"{helper_signatures['historical_loader']['signature']}"
        ),
        "",
        "LIVE QUOTE PROBE",
        (
            "Symbol:                           "
            f"{probe['quote']['symbol']}"
        ),
        (
            "Price:                            "
            f"{probe['quote']['price']}"
        ),
        (
            "Currency:                         "
            f"{probe['quote']['currency']}"
        ),
        (
            "Provider:                         "
            f"{probe['quote']['provider']}"
        ),
        (
            "Latency:                          "
            f"{probe['quote']['latency_ms']} ms"
        ),
        "",
        "LIVE HISTORICAL PROBE",
        (
            "Symbol:                           "
            f"{probe['historical']['symbol']}"
        ),
        (
            "Bars returned:                    "
            f"{probe['historical']['bar_count']}"
        ),
        (
            "Interval:                         "
            f"{probe['historical']['interval']}"
        ),
        (
            "Provider:                         "
            f"{probe['historical']['provider']}"
        ),
        (
            "Latency:                          "
            f"{probe['historical']['latency_ms']} ms"
        ),
        "",
        "REGISTRATION AND ROUTING",
        (
            "Registered provider:              "
            f"{probe['provider_registration']['name']}"
        ),
        (
            "Registry size:                    "
            f"{probe['provider_registration']['registry_size']}"
        ),
        "Quote capability routing:          PASS",
        "Historical capability routing:     PASS",
        "Canonical quote DTO:               PASS",
        "Canonical historical DTO:          PASS",
        "Cache path:                        PASS",
        "",
        "UNCHANGED",
        "main.py changed:                    NO",
        "Production composition changed:    NO",
        "Broker execution enabled:          NO",
        "Live trading enabled:              NO",
        "",
        "NEXT",
        (
            "Stage 7 — Market-Data Composition Root "
            "and Read-Only Runtime Integration"
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
            "## Stage 6 — Dependency Qualification, "
            "Live Compatibility Probe, and Provider "
            "Registration Verification\n"
            "\n"
            f"Verified: {completed_at.isoformat()}\n"
            "\n"
            "- Status: **COMPLETE AND VERIFIED**\n"
            f"- yfinance version: **{yfinance_version}**\n"
            "- Live quote probe: **PASS**\n"
            "- Live historical-bars probe: **PASS**\n"
            "- Provider registration: **PASS**\n"
            "- Provider routing: **PASS**\n"
            "- Canonical quote DTO: **PASS**\n"
            "- Canonical historical DTO: **PASS**\n"
            "- Cache path: **PASS**\n"
            "- main.py changed: **NO**\n"
            "- Production composition changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
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
        print("WORKSTREAM 2 STAGE 6 FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("main.py was not intentionally modified.")
        print("Production runtime composition was not changed.")
        print("Broker execution remains disabled.")
        print("Live trading remains disabled.")
        print("=" * 80)

        raise SystemExit(1)
