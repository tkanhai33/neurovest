
"""NeuroVest consolidated read-only financial analysis candidate.

The authenticated owner ID MUST come from a trusted backend
authentication dependency, never from user-submitted JSON.

Does not establish database ownership or expose a public route.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path


class FinancialAnalysisDenied(RuntimeError):
    pass


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path, expected):
    if (
        not path.is_file()
        or path.is_symlink()
        or _digest(path) != expected
    ):
        raise FinancialAnalysisDenied("engine_integrity_failed")

    name = "neurovest_b13_freshness_engine"
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise FinancialAnalysisDenied("engine_loader_failed")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def analyze_authenticated_owner(
    *,
    authenticated_owner_id,
    owned_resource_owner_id,
    primary_symbol,
    universe_symbols,
    proposal,
    provider_loader,
    analysis_mode,
    engine_paths,
    expected_hashes,
    as_of=None,
):
    """Analyze already-authorized owner data; never fetch accounts.

    Both owner identifiers must be supplied by trusted backend
    authentication and ownership-resolution code.
    """

    if (
        not isinstance(authenticated_owner_id, str)
        or not authenticated_owner_id.strip()
        or not isinstance(owned_resource_owner_id, str)
        or authenticated_owner_id != owned_resource_owner_id
    ):
        raise FinancialAnalysisDenied("owner_scope_denied")

    if analysis_mode not in (
        "HISTORICAL_RESEARCH",
        "CURRENT_MARKET_ANALYSIS",
    ):
        raise FinancialAnalysisDenied("invalid_analysis_mode")

    if (
        not isinstance(universe_symbols, (tuple, list))
        or not 2 <= len(universe_symbols) <= 12
        or not all(
            isinstance(symbol, str)
            and symbol.isascii()
            and symbol.isupper()
            and symbol.isalnum()
            and 1 <= len(symbol) <= 10
            for symbol in universe_symbols
        )
        or len(set(universe_symbols)) != len(universe_symbols)
        or primary_symbol not in universe_symbols
    ):
        raise FinancialAnalysisDenied("invalid_owner_universe")

    if not callable(provider_loader):
        raise FinancialAnalysisDenied("provider_loader_required")

    if set(engine_paths) != {"B1", "B2", "B3", "B5"}:
        raise FinancialAnalysisDenied("engine_manifest_invalid")

    if set(expected_hashes) != set(engine_paths):
        raise FinancialAnalysisDenied("engine_manifest_invalid")

    for label, path in engine_paths.items():
        if (
            not isinstance(path, Path)
            or not path.is_file()
            or path.is_symlink()
            or _digest(path) != expected_hashes[label]
        ):
            raise FinancialAnalysisDenied(
                "engine_integrity_failed"
            )

    if as_of is None:
        as_of = datetime.now(timezone.utc)

    b5 = _load(engine_paths["B5"], expected_hashes["B5"])

    result = b5.evaluate_with_freshness(
        analysis_mode=analysis_mode,
        primary_symbol=primary_symbol,
        universe_symbols=list(universe_symbols),
        proposal=proposal,
        provider_loader=provider_loader,
        b1_candidate=engine_paths["B1"],
        b2_candidate=engine_paths["B2"],
        b3_candidate=engine_paths["B3"],
        b1_sha256=expected_hashes["B1"],
        b2_sha256=expected_hashes["B2"],
        b3_sha256=expected_hashes["B3"],
        as_of=as_of,
    )

    for field in (
        "execution_enabled",
        "order_admission_allowed",
        "live_trading_authorized",
    ):
        if result.get(field) is not False:
            raise FinancialAnalysisDenied(
                "unsafe_engine_response"
            )

    return {
        "analysis_mode": result["analysis_mode"],
        "primary_symbol": primary_symbol,
        "universe_symbols": list(universe_symbols),
        "actual_v4_evaluator_count": (
            result["actual_v4_evaluator_count"]
        ),
        "strategy_aggregation": result["strategy_aggregation"],
        "portfolio_evaluation": result["portfolio_evaluation"],
        "freshness": result["freshness"],
        "analysis_evidence_sha256": (
            result.get("analysis_evidence_sha256")
        ),
        "current_market_data_age_qualified": (
            result["current_market_data_age_qualified"]
        ),
        "execution_enabled": False,
        "order_admission_allowed": False,
        "live_trading_authorized": False,
        "source_freshness_independently_verified": False,
        "live_quote_freshness_verified": False,
        "evaluation_type": "FIXED_WEIGHT_HISTORICAL_SNAPSHOT",
        "api_exposure_authorized": False,
    }
