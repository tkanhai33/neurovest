"""NeuroVest B5: historical/current market-analysis boundary.

Read-only analysis. No order creation, ledger writes or broker calls.
"""

from __future__ import annotations

import hashlib
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping


class MarketFreshnessUnavailable(RuntimeError):
    pass


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path, expected):
    if (
        not path.is_file()
        or path.is_symlink()
        or sha(path) != expected
    ):
        raise MarketFreshnessUnavailable(
            "candidate_integrity_failure"
        )

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise MarketFreshnessUnavailable(
            "candidate_loader_unavailable"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timestamp(value):
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            raise MarketFreshnessUnavailable(
                "invalid_timestamp"
            ) from None
    else:
        raise MarketFreshnessUnavailable(
            "invalid_timestamp"
        )

    if dt.tzinfo is None or dt.utcoffset() is None:
        raise MarketFreshnessUnavailable(
            "naive_timestamp"
        )

    return dt.astimezone(timezone.utc)


def inspect_freshness(
    *,
    universe_bars,
    as_of,
    max_age_days=7,
):
    now = timestamp(as_of)

    if (
        isinstance(max_age_days, bool)
        or not isinstance(max_age_days, int)
        or not 1 <= max_age_days <= 30
    ):
        raise MarketFreshnessUnavailable(
            "invalid_freshness_window"
        )

    if not isinstance(universe_bars, Mapping) or not universe_bars:
        raise MarketFreshnessUnavailable(
            "invalid_market_universe"
        )

    observations = {}
    stale = []

    for symbol, bars in universe_bars.items():
        if (
            not isinstance(symbol, str)
            or not isinstance(bars, (list, tuple))
            or not bars
        ):
            raise MarketFreshnessUnavailable(
                "invalid_market_history"
            )

        parsed = []

        for bar in bars:
            if not isinstance(bar, Mapping):
                raise MarketFreshnessUnavailable(
                    "invalid_market_bar"
                )

            observed = timestamp(bar.get("timestamp"))

            if observed > now:
                raise MarketFreshnessUnavailable(
                    "future_dated_market_bar"
                )

            parsed.append(observed)

        if parsed != sorted(parsed):
            raise MarketFreshnessUnavailable(
                "unordered_market_history"
            )

        if len(parsed) != len(set(parsed)):
            raise MarketFreshnessUnavailable(
                "duplicate_market_timestamp"
            )

        latest = parsed[-1]
        age = (now.date() - latest.date()).days

        observations[symbol] = {
            "latest_observation_utc": latest.isoformat(),
            "age_calendar_days": age,
        }

        if age > max_age_days:
            stale.append(symbol)

    return {
        "as_of_utc": now.isoformat(),
        "max_age_calendar_days": max_age_days,
        "symbols": observations,
        "stale_symbols": sorted(stale),
        "within_age_window": not stale,
        "source_freshness_independently_verified": False,
        "live_quote_freshness_verified": False,
        "exchange_calendar_verified": False,
    }


def evaluate_with_freshness(
    *,
    analysis_mode,
    primary_symbol,
    universe_symbols,
    proposal,
    provider_loader: Callable,
    b1_candidate: Path,
    b2_candidate: Path,
    b3_candidate: Path,
    b1_sha256: str,
    b2_sha256: str,
    b3_sha256: str,
    as_of,
    max_age_days=7,
    transaction_cost_bps=10.0,
):
    if analysis_mode not in (
        "HISTORICAL_RESEARCH",
        "CURRENT_MARKET_ANALYSIS",
    ):
        raise MarketFreshnessUnavailable(
            "invalid_analysis_mode"
        )

    if not callable(provider_loader):
        raise MarketFreshnessUnavailable(
            "provider_loader_required"
        )

    # Validate every dependency before calling the provider.
    for path, expected in (
        (b1_candidate, b1_sha256),
        (b2_candidate, b2_sha256),
        (b3_candidate, b3_sha256),
    ):
        if (
            not path.is_file()
            or path.is_symlink()
            or sha(path) != expected
        ):
            raise MarketFreshnessUnavailable(
                "dependency_integrity_failure"
            )

    try:
        bars = provider_loader(universe_symbols, limit=253)
    except Exception as exc:
        raise MarketFreshnessUnavailable(
            "provider_failure:" + type(exc).__name__
        ) from exc

    if (
        not isinstance(bars, dict)
        or set(bars) != set(universe_symbols)
    ):
        raise MarketFreshnessUnavailable(
            "provider_universe_incomplete"
        )

    freshness = inspect_freshness(
        universe_bars=bars,
        as_of=as_of,
        max_age_days=max_age_days,
    )

    if (
        analysis_mode == "CURRENT_MARKET_ANALYSIS"
        and not freshness["within_age_window"]
    ):
        raise MarketFreshnessUnavailable(
            "stale_market_history"
        )

    b3 = load(
        "neuro_B5_verified_B3",
        b3_candidate,
        b3_sha256,
    )

    # Reuse the captured observations. Never trigger another
    # network request from the downstream coordinator.
    def captured_loader(symbols, *, limit):
        if (
            list(symbols) != list(universe_symbols)
            or limit != 253
        ):
            raise MarketFreshnessUnavailable(
                "unexpected_downstream_request"
            )
        return bars

    result = b3.evaluate_provider_universe(
        primary_symbol=primary_symbol,
        universe_symbols=universe_symbols,
        proposal=proposal,
        b1_candidate=b1_candidate,
        b2_candidate=b2_candidate,
        b1_expected_sha256=b1_sha256,
        b2_expected_sha256=b2_sha256,
        provider_loader=captured_loader,
        transaction_cost_bps=transaction_cost_bps,
    )

    if (
        result.get("execution_enabled") is not False
        or result.get("order_admission_allowed") is not False
        or result.get("live_trading_authorized") is not False
    ):
        raise MarketFreshnessUnavailable(
            "unsafe_analysis_result"
        )

    result = dict(result)
    result["analysis_mode"] = analysis_mode
    result["freshness"] = freshness
    result["current_market_data_age_qualified"] = (
        analysis_mode == "CURRENT_MARKET_ANALYSIS"
        and freshness["within_age_window"]
    )
    result["live_quote_freshness_verified"] = False
    result["source_freshness_independently_verified"] = False
    result["risk_execution_authorized"] = False
    result["order_admission_allowed"] = False
    result["broker_order_generation_enabled"] = False
    result["execution_enabled"] = False
    result["live_trading_authorized"] = False
    result["limitations"] = [
        "Historical bar timestamps are not live quotes",
        "Recent observations do not independently prove provider provenance",
        "Seven calendar days is a conservative age policy, not an exchange calendar",
        "Portfolio evaluation is not a strategy backtest",
        "No authoritative account or execution-risk authorization",
    ]

    return result
