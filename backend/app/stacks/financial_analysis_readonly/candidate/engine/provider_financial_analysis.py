"""B3: read-only market-data to financial-analysis bridge.

Never submits orders, accesses the ledger, or grants execution
authorization. Provider access must be explicitly selected.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Callable


class ProviderAnalysisUnavailable(RuntimeError):
    pass


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str, path: Path):
    if not path.is_file() or path.is_symlink():
        raise ProviderAnalysisUnavailable("candidate_missing")

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise ProviderAnalysisUnavailable("loader_unavailable")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_provider_universe(
    *,
    primary_symbol: str,
    universe_symbols: list[str],
    proposal: object,
    b1_candidate: Path,
    b2_candidate: Path,
    b1_expected_sha256: str,
    b2_expected_sha256: str,
    provider_loader: Callable | None = None,
    allow_provider_network: bool = False,
    rebalance_interval_bars: int = 21,
    transaction_cost_bps: float = 10.0,
) -> dict:

    for path, expected in (
        (b1_candidate, b1_expected_sha256),
        (b2_candidate, b2_expected_sha256),
    ):
        if (
            not path.is_file()
            or path.is_symlink()
            or _hash(path) != expected
        ):
            raise ProviderAnalysisUnavailable(
                "candidate_integrity_failure"
            )

    if (
        not isinstance(universe_symbols, list)
        or not 2 <= len(universe_symbols) <= 12
        or any(
            not isinstance(symbol, str)
            or not symbol
            or symbol != symbol.strip().upper()
            for symbol in universe_symbols
        )
        or len(set(universe_symbols)) != len(universe_symbols)
        or primary_symbol not in universe_symbols
    ):
        raise ProviderAnalysisUnavailable(
            "invalid_symbol_universe"
        )

    if provider_loader is None:
        if not allow_provider_network:
            raise ProviderAnalysisUnavailable(
                "network_provider_not_authorized"
            )

        from backend.app.stacks.market_data.multi_symbol_bars import (
            get_daily_bars_for_symbols,
        )

        provider_loader = get_daily_bars_for_symbols
        origin = "EXISTING_MARKET_DATA_PROVIDER"
    else:
        if allow_provider_network:
            raise ProviderAnalysisUnavailable(
                "ambiguous_provider_mode"
            )
        origin = "INJECTED_TEST_PROVIDER"

    try:
        bars = provider_loader(
            universe_symbols,
            limit=253,
        )
    except Exception as exc:
        raise ProviderAnalysisUnavailable(
            "provider_retrieval_failed:"
            + type(exc).__name__
        ) from exc

    if not isinstance(bars, dict):
        raise ProviderAnalysisUnavailable(
            "provider_contract_invalid"
        )

    if set(bars) != set(universe_symbols):
        raise ProviderAnalysisUnavailable(
            "provider_symbols_incomplete"
        )

    b2 = _load("neuro_B3_verified_B2", b2_candidate)

    try:
        analysis = b2.evaluate(
            primary_symbol=primary_symbol,
            universe_bars=bars,
            proposal=proposal,
            b1_candidate=b1_candidate,
            rebalance_interval_bars=rebalance_interval_bars,
            transaction_cost_bps=transaction_cost_bps,
        )
    except Exception as exc:
        raise ProviderAnalysisUnavailable(
            "integrated_analysis_failed:"
            + type(exc).__name__
        ) from exc

    if (
        analysis.get("actual_v4_evaluator_count") != 15
        or analysis.get("execution_enabled") is not False
        or analysis.get("order_admission_allowed") is not False
        or analysis.get("broker_order_generation_enabled")
            is not False
        or analysis.get("live_trading_authorized") is not False
    ):
        raise ProviderAnalysisUnavailable(
            "unsafe_analysis_output"
        )

    result = dict(analysis)

    # B2 hardcodes fixture origin; overwrite it with the
    # accurately observed retrieval mode.
    result["data_origin"] = origin
    result["provider_retrieval_completed"] = True
    result["live_market_data_verified"] = False
    result["provider_data_read_only"] = True
    result["b1_candidate_sha256"] = b1_expected_sha256
    result["b2_candidate_sha256"] = b2_expected_sha256
    result["execution_enabled"] = False
    result["order_admission_allowed"] = False
    result["live_trading_authorized"] = False

    result["limitations"] = [
        "Provider retrieval does not establish quote freshness",
        "Historical allocation evaluation is not a strategy backtest",
        "No authoritative owner account or ledger risk assessment",
        "No order admission or broker authorization",
    ]

    return result
