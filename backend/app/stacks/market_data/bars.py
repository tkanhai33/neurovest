"""Truthful historical-bar compatibility boundary.

This module preserves the legacy ``get_bars(symbol, limit)`` surface while
routing every live request through NeuroVest's canonical read-only market-data
runtime. It never manufactures, randomizes, or substitutes market history.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from math import ceil
from typing import Any

from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
)
from backend.app.stacks.market_data.runtime_composition import (
    get_market_data_runtime,
)


class HistoricalBarsUnavailableError(RuntimeError):
    """Canonical providers could not supply truthful historical bars."""


class HistoricalBarsInsufficientDataError(
    HistoricalBarsUnavailableError
):
    """The provider returned fewer real observations than requested."""


def _normalized_limit(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError(
            "historical bar limit must be an integer"
        )

    if limit <= 0:
        raise ValueError(
            "historical bar limit must be greater than zero"
        )

    if limit > 5000:
        raise ValueError(
            "historical bar limit must not exceed 5000"
        )

    return limit


def _calendar_lookback_days(limit: int) -> int:
    """Allow for weekends, holidays, and ordinary market closures."""

    return max(
        30,
        int(
            ceil(
                limit * 2.75
            )
        ) + 30,
    )


def _legacy_bar_record(
    bar: HistoricalBar,
    *,
    include_adjusted_close: bool = False,
) -> dict[str, Any]:
    record = {
        "symbol": bar.symbol,
        "timestamp": bar.timestamp.isoformat(),
        "interval": bar.interval,
        "open": float(bar.open),
        "high": float(bar.high),
        "low": float(bar.low),
        "close": float(bar.close),
        "volume": float(bar.volume),
        "provider": bar.provider,
    }
    if include_adjusted_close:
        record["adjusted_close"] = (
            float(bar.adjusted_close)
            if bar.adjusted_close is not None
            else None
        )
    return record


def get_bars(
    symbol: str,
    limit: int = 5,
    *,
    include_adjusted_close: bool = False,
) -> list[dict[str, Any]]:
    """Return exactly ``limit`` real normalized daily OHLCV observations.

    Provider, routing, normalization, caching, and failover remain owned by
    the canonical market-data runtime. Provider failure and insufficient
    history fail closed. No synthetic or fabricated observations are allowed.
    """

    normalized_symbol = str(
        symbol
    ).strip().upper()

    if not normalized_symbol:
        raise ValueError(
            "historical bar symbol must not be empty"
        )

    normalized_limit = _normalized_limit(
        limit
    )

    end = datetime.now(
        UTC
    )

    start = end - timedelta(
        days=_calendar_lookback_days(
            normalized_limit
        )
    )

    request = HistoricalBarsRequest(
        symbol=normalized_symbol,
        start=start,
        end=end,
        interval="1d",
        adjusted=True,
        limit=normalized_limit,
    )

    try:
        runtime = get_market_data_runtime()

        result = runtime.router.get_historical_bars(
            request
        )

    except Exception as exc:
        raise HistoricalBarsUnavailableError(
            "truthful historical bars are unavailable for "
            f"{normalized_symbol}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if not isinstance(
        result,
        HistoricalBarsResult,
    ):
        raise HistoricalBarsUnavailableError(
            "canonical market-data router returned a "
            "non-canonical historical result"
        )

    real_bars = tuple(
        result.bars
    )

    if len(real_bars) < normalized_limit:
        raise HistoricalBarsInsufficientDataError(
            "insufficient truthful historical bars for "
            f"{normalized_symbol}: requested "
            f"{normalized_limit}, received {len(real_bars)}"
        )

    selected = real_bars[
        -normalized_limit:
    ]

    return [
        _legacy_bar_record(
            bar,
            include_adjusted_close=include_adjusted_close,
        )
        for bar in selected
    ]


def healthcheck() -> dict[str, object]:
    """Describe the adapter without loading or calling a provider."""

    return {
        "component":
            "truthful_historical_bars_compatibility",

        "healthy":
            True,

        "provider_owner":
            "canonical_market_data_runtime",

        "interval":
            "1d",

        "fabricated_fallback":
            False,

        "network_called":
            False,
    }
