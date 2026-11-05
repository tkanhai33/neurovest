from __future__ import annotations

import dataclasses
import json
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
    HistoricalBarsResult,
)

from backend.app.stacks.chat_public import (
    financial_research_13d_r58 as financial,
)

VERSION = "NEUROVEST_13D_R62_HISTORICAL_INTELLIGENCE"

HISTORY_INTENT = re.compile(
    r"\b(?:historical|price history|"
    r"price performance|market performance|"
    r"stock performance|performance over|"
    r"past month|past year|last month|"
    r"last year|last [0-9]+ days|"
    r"past [0-9]+ days|"
    r"three.month|six.month|"
    r"30.day|90.day|180.day|"
    r"52.week|one.year|"
    r"price trend|market trend|"
    r"return over|returns over)\b",
    re.I,
)

PERIODS = (
    (re.compile(r"\b(?:one.year|1.year|52.week|"
                r"last year|past year)\b", re.I), 365),
    (re.compile(r"\b(?:six.month|6.month|"
                r"180.day)\b", re.I), 180),
    (re.compile(r"\b(?:three.month|3.month|"
                r"90.day)\b", re.I), 90),
    (re.compile(r"\b(?:one.month|1.month|"
                r"30.day|last month|past month)\b", re.I), 30),
)

MAX_BARS = 550

def requested_days(message):
    match = re.search(
        r"\b(?:last|past)\s+([0-9]{1,3})\s+days\b",
        message,
        re.I,
    )

    if match:
        return max(2, min(365, int(match.group(1))))

    for pattern, days in PERIODS:
        if pattern.search(message):
            return days

    return 90

def _get(item, field):
    if isinstance(item, dict):
        return item.get(field)

    return getattr(item, field, None)

def _number(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("invalid_number")

    number = Decimal(str(value))

    if not number.is_finite():
        raise ValueError("nonfinite_number")

    return number

def _format(value):
    return format(value.normalize(), "f")

def _date_text(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]

    if isinstance(value, str):
        try:
            date.fromisoformat(value[:10])
            return value[:10]
        except ValueError:
            return None

    return None

def analyze_bars(bars):
    if not isinstance(bars, (tuple, list)):
        raise ValueError("invalid_bar_collection")

    if len(bars) > MAX_BARS:
        raise ValueError("too_many_bars")

    cleaned = []

    for bar in bars:
        timestamp = next(
            (
                _get(bar, name)
                for name in (
                    "timestamp", "time", "date",
                    "datetime", "observed_at", "bar_time",
                    "start"
                )
                if _get(bar, name) is not None
            ),
            None,
        )

        close = next(
            (
                _get(bar, name)
                for name in (
                    "close", "adjusted_close", "adj_close",
                    "closing_price"
                )
                if _get(bar, name) is not None
            ),
            None,
        )

        text = _date_text(timestamp)

        if text is None or close is None:
            continue

        try:
            number = _number(close)
        except (ValueError, InvalidOperation):
            continue

        if number <= 0:
            continue

        cleaned.append((text, number))

    if len(cleaned) < 2:
        raise ValueError("insufficient_valid_bars")

    cleaned.sort(key=lambda item: item[0])

    # Reject duplicate dates instead of silently counting
    # multiple observations as separate daily closes.
    if len({x[0] for x in cleaned}) != len(cleaned):
        raise ValueError("duplicate_bar_dates")

    first_date, first = cleaned[0]
    last_date, last = cleaned[-1]

    high = max(value for _, value in cleaned)
    low = min(value for _, value in cleaned)

    with localcontext() as ctx:
        ctx.prec = 28

        change = last - first
        percent = change / first * Decimal(100)

    return {
        "first_observation_date": first_date,
        "last_observation_date": last_date,
        "observations": len(cleaned),
        "first_close": _format(first),
        "last_close": _format(last),
        "close_change": _format(change),
        "close_return_percent": _format(percent),
        "highest_observed_close": _format(high),
        "lowest_observed_close": _format(low),
        "trend": (
            "higher" if last > first else
            "lower" if last < first else
            "unchanged"
        ),
        "return_type": "price_return_excluding_dividends",
        "note": (
            "Return is calculated from first and last "
            "available closes, not necessarily exact "
            "calendar endpoints. Adjustment policy "
            "depends on the canonical provider."
        ),
    }

def build_request(symbol, start, end):
    import inspect

    parameters = inspect.signature(
        HistoricalBarsRequest
    ).parameters

    values = {
        "symbol": symbol,
        "start": start,
        "end": end,
        "interval": "1d",
    }

    if "adjusted" in parameters:
        values["adjusted"] = True

    if "limit" in parameters:
        values["limit"] = MAX_BARS

    return HistoricalBarsRequest(**values)

def collect_historical_evidence(
    message,
    *,
    history_loader=None,
    now=None,
):
    if not isinstance(message, str):
        return None

    if not message.strip() or len(message) > 500:
        return None

    if not HISTORY_INTENT.search(message):
        return None

    companies = financial.companies_in_text(message)

    if not companies:
        return None

    if history_loader is None:
        from backend.app.stacks.market_data.runtime_composition import (
            get_market_data_runtime,
        )

        history_loader = (
            get_market_data_runtime()
            .router.get_historical_bars
        )

    end = now or datetime.now(timezone.utc)

    if isinstance(end, date) and not isinstance(
        end, datetime
    ):
        end = datetime(
            end.year, end.month, end.day,
            tzinfo=timezone.utc,
        )

    days = requested_days(message)

    # A few extra calendar days account for weekends,
    # holidays, and differing market calendars.
    start = end - timedelta(days=days + 7)

    results = []

    for ticker, _ in companies[:2]:
        try:
            request = build_request(
                ticker, start, end
            )

            response = history_loader(request)

            if not isinstance(
                response, HistoricalBarsResult
            ):
                raise ValueError(
                    "noncanonical_historical_result"
                )

            bars = response.bars
            metrics = analyze_bars(bars)

            metadata = {}
            for field in (
                "provider", "symbol",
                "interval", "currency",
                "adjusted", "as_of",
            ):
                value = getattr(
                    response, field, None
                )

                if isinstance(
                    value, (str, int, float, bool)
                ):
                    metadata[field] = value

            # R63: Preserve the canonical result's evidence
            # integrity indicators without exposing raw
            # provider objects or unrestricted metadata.
            complete = getattr(response, "complete", None)
            fetched_at = getattr(response, "fetched_at", None)
            warnings = getattr(response, "warnings", ())

            metadata["complete"] = (
                complete if isinstance(complete, bool)
                else None
            )

            if hasattr(fetched_at, "isoformat"):
                metadata["fetched_at"] = fetched_at.isoformat()
            elif isinstance(fetched_at, str):
                metadata["fetched_at"] = fetched_at[:80]
            else:
                metadata["fetched_at"] = None

            metadata["warnings"] = [
                str(item)[:160]
                for item in (
                    warnings
                    if isinstance(warnings, (list, tuple))
                    else ()
                )[:8]
            ]

            if metadata["complete"] is False:
                metadata["data_quality"] = "incomplete"
            elif metadata["complete"] is True:
                metadata["data_quality"] = "provider_complete"
            else:
                metadata["data_quality"] = "unknown"

            results.append({
                "ticker": ticker,
                "status": "ok",
                "metrics": metrics,
                "provider_metadata": metadata,
            })

        except Exception:
            results.append({
                "ticker": ticker,
                "status": "unavailable",
                "reason": (
                    "Historical data unavailable, "
                    "incompatible, or insufficient"
                ),
            })

    return {
        "capability": "historical_price_analysis",
        "source": (
            "NeuroVest canonical market-data router"
        ),
        "requested_calendar_days": days,
        "requested_start": start.date().isoformat(),
        "requested_end": end.date().isoformat(),
        "results": results,
        "live_trading": False,
        "limitations": (
            "Historical closing prices, not a live quote. "
            "No dividends, fees, or investment advice "
            "are implied by price-only returns."
        ),
    }

def attach_historical_evidence(
    context,
    message,
    *,
    history_loader=None,
    now=None,
):
    if not isinstance(context, str):
        return context

    if VERSION in context or len(context) > 48000:
        return context

    result = collect_historical_evidence(
        message,
        history_loader=history_loader,
        now=now,
    )

    if result is None:
        return context

    payload = json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    if len(payload) > 5000:
        return context

    return (
        context
        + "\n\n[" + VERSION + "]\n"
        + "CANONICAL HISTORICAL MARKET EVIDENCE\n"
        + payload
        + "\nExplain observed historical performance "
        + "with dates and provider limitations. "
        + "Distinguish price returns from total "
        + "returns and market quotations. "
        + "Do not invent missing bars, prices, "
        + "dividends, timestamps or other data. "
        + "No broker or execution permission."
        + "\n[/" + VERSION + "]"
    )
