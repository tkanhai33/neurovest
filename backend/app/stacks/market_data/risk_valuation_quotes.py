"""Fail-closed intraday bar quotes for paper-risk valuation.

A price is paired with the timestamp of its actual source bar.
Retrieval time is NEVER treated as the market observation time.

This adapter does not authorize trading or establish exchange-grade
market-data guarantees.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


class RiskQuoteUnavailable(RuntimeError):
    """A source-grounded risk valuation quote is unavailable."""


def _currency(value: object) -> str:
    if not isinstance(value, str):
        raise RiskQuoteUnavailable("quote_currency_unavailable")

    code = value.strip().upper()

    if (
        len(code) != 3
        or not code.isascii()
        or not code.isalpha()
    ):
        raise RiskQuoteUnavailable("quote_currency_invalid")

    return code


def _price(value: object) -> str:
    if value is None or isinstance(value, bool):
        raise RiskQuoteUnavailable("quote_price_unavailable")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise RiskQuoteUnavailable("quote_price_invalid") from None

    if not number.is_finite() or number <= 0:
        raise RiskQuoteUnavailable("quote_price_invalid")

    return str(number)


def _observed_at(value: object) -> datetime:
    # datetime-compatible pandas Timestamp is accepted;
    # numeric epoch guesses and naive datetimes are not.
    if not isinstance(value, datetime):
        raise RiskQuoteUnavailable(
            "source_bar_timestamp_unavailable"
        )

    if value.tzinfo is None or value.utcoffset() is None:
        raise RiskQuoteUnavailable(
            "source_bar_timestamp_not_timezone_aware"
        )

    return value.astimezone(timezone.utc)


def normalize_risk_bar_quote(
    symbol: str,
    payload: object,
) -> dict:
    """Validate fields without supplying any missing provenance."""
    if (
        not isinstance(symbol, str)
        or not symbol.strip()
    ):
        raise RiskQuoteUnavailable("symbol_unavailable")

    requested = symbol.strip().upper()

    if not isinstance(payload, Mapping):
        raise RiskQuoteUnavailable("source_payload_unavailable")

    received = payload.get("symbol")

    if (
        not isinstance(received, str)
        or received.strip().upper() != requested
    ):
        raise RiskQuoteUnavailable("source_symbol_mismatch")

    if payload.get("provider") != "yfinance":
        raise RiskQuoteUnavailable("source_provider_unverified")

    return {
        "status": "ok",
        "symbol": requested,
        "price": _price(payload.get("price")),
        "currency": _currency(payload.get("currency")),
        "observed_at": _observed_at(
            payload.get("observed_at")
        ),
        "provider": "yfinance",
    }


def _fetch_intraday_source_bar(symbol: str) -> dict:
    """Synchronous yfinance operation, run in a worker thread."""
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)

        # The close price and timestamp MUST come from the
        # same source row. Do not combine fast_info last_price
        # with a historical timestamp.
        bars = ticker.history(
            period="1d",
            interval="1m",
            auto_adjust=False,
        )

        if (
            bars is None
            or bars.empty
            or "Close" not in bars.columns
        ):
            raise RiskQuoteUnavailable(
                "source_intraday_bars_unavailable"
            )

        close_series = bars["Close"].dropna()

        if close_series.empty:
            raise RiskQuoteUnavailable(
                "source_intraday_close_unavailable"
            )

        index = close_series.index[-1]
        price = close_series.iloc[-1]

        # The index represents the provider's bar time,
        # not the time NeuroVest downloaded the data.
        if not isinstance(index, datetime):
            raise RiskQuoteUnavailable(
                "source_bar_timestamp_unavailable"
            )

        fast_info = ticker.fast_info
        currency = None

        if fast_info is not None:
            try:
                currency = fast_info.get("currency")
            except (AttributeError, KeyError, TypeError, ValueError):
                currency = None

        if not currency:
            try:
                info = ticker.info
                if isinstance(info, Mapping):
                    currency = info.get("currency")
            except Exception:
                currency = None

        return {
            "symbol": symbol,
            "price": price,
            "currency": currency,
            "observed_at": index,
            "provider": "yfinance",
        }

    except RiskQuoteUnavailable:
        raise
    except Exception as exc:
        raise RiskQuoteUnavailable(
            "intraday_provider_request_failed"
        ) from exc


async def get_risk_valuation_quote(
    symbol: str,
    *,
    source_loader: Callable[[str], Any] | None = None,
) -> dict:
    """Return a checked quote for the existing equity verifier.

    An injected source_loader is for controlled offline testing.
    Production uses the actual source-bar fetcher.
    """
    if (
        not isinstance(symbol, str)
        or not symbol.strip()
    ):
        raise RiskQuoteUnavailable("symbol_unavailable")

    normalized = symbol.strip().upper()

    fetch = (
        _fetch_intraday_source_bar
        if source_loader is None
        else source_loader
    )

    if not callable(fetch):
        raise RiskQuoteUnavailable("source_loader_invalid")

    payload = await asyncio.to_thread(fetch, normalized)

    return normalize_risk_bar_quote(
        normalized,
        payload,
    )
