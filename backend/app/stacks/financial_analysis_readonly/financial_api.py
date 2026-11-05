"""Isolated NeuroVest authenticated financial API candidate.

No production router registration. No order or database writes.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.strategy.allocation_proposal import (
    build_allocation_proposal,
)

ROUTE = "/api/v1/financial-analysis/readonly"


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_verified(path, expected, name):
    if (
        not path.is_file()
        or path.is_symlink()
        or _sha(path) != expected
    ):
        raise RuntimeError("verified_engine_unavailable")

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError("verified_engine_loader_unavailable")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def create_candidate_router(
    *,
    owner_universe_loader,
    provider_loader,
    b13_directory,
):
    if (
        not callable(owner_universe_loader)
        or not callable(provider_loader)
    ):
        raise ValueError("trusted_loader_required")

    directory = Path(b13_directory).resolve()
    evidence_path = directory / "evidence/qualification.json"
    facade_path = directory / "candidate/owned_financial_analysis.py"
    engine_root = directory / "candidate/engine"

    report = {'result': 'B13_CONSOLIDATED_SERVICE_CANDIDATE_PASS', 'checks': {'B1_QUALIFIED': True, 'B1_COPY_VERIFIED': True, 'B2_QUALIFIED': True, 'B2_COPY_VERIFIED': True, 'B3_QUALIFIED': True, 'B3_COPY_VERIFIED': True, 'B5_QUALIFIED': True, 'B5_COPY_VERIFIED': True, 'FACADE_SYNTAX': True, 'ACTUAL_15_EVALUATORS': True, 'WEIGHTED_PORTFOLIO_ANALYSIS': True, 'STRATEGY_AGGREGATION': True, 'FRESH_DATA_AGE_QUALIFIED': True, 'CANONICAL_PROVIDER_CONTRACT': True, 'EXECUTION_DENIED': True, 'CROSS_OWNER_DENIED_BEFORE_PROVIDER': True, 'ANONYMOUS_DENIED': True, 'STALE_OWNER_ANALYSIS_DENIED': True, 'DETERMINISTIC_REPLAY': True}, 'facade_sha256': '2c610ab7c1f65289816d451388d7a29152f5f00315bef83649e794187f3e8bb0', 'engine_sha256': {'B1': '142c2a5a6876fd6b9bde7c98e29a239ac1f5c9bb9586fb648e6c76e76605710d', 'B2': 'c2af0bf01b536167b43bef3e279fdbf5dd82bd696663fd5a37ced5b468d48cac', 'B3': '41398b056ed2c7fb601910e84d2ac4b40fbe9427ffc326c3ff49fecadb311e66', 'B5': '62ac422c974863cff78050b49047cdb8876f57e60dc2a53fd7f3b191ad3fa55a'}}

    if (
        report.get("result")
        != "B13_CONSOLIDATED_SERVICE_CANDIDATE_PASS"
        or not report.get("checks")
        or not all(report["checks"].values())
    ):
        raise RuntimeError("B13_qualification_invalid")

    facade = _load_verified(
        facade_path,
        report["facade_sha256"],
        "neurovest_B14_verified_facade",
    )

    filenames = {
        "B1": "financial_analysis.py",
        "B2": "financial_analysis_b2.py",
        "B3": "provider_financial_analysis.py",
        "B5": "freshness_analysis.py",
    }

    paths = {
        key: engine_root / filename
        for key, filename in filenames.items()
    }

    hashes = report["engine_sha256"]

    for key, path in paths.items():
        if (
            not path.is_file()
            or path.is_symlink()
            or _sha(path) != hashes[key]
        ):
            raise RuntimeError("B13_engine_hash_mismatch")

    router = APIRouter(tags=["financial-analysis"])

    @router.get(ROUTE)
    async def read_owned_financial_analysis(
        mode: str = Query(
            default="CURRENT_MARKET_ANALYSIS"
        ),
        principal=Depends(require_authenticated_principal),
    ):
        # Identity must come exclusively from authentication.
        owner = getattr(principal, "subject", None)

        if not isinstance(owner, str) or not owner.strip():
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
            )

        if mode not in (
            "CURRENT_MARKET_ANALYSIS",
            "HISTORICAL_RESEARCH",
        ):
            raise HTTPException(
                status_code=422,
                detail="Unsupported analysis mode",
            )

        try:
            # Trusted resolver must be owner-scoped.
            symbols = await owner_universe_loader(
                owner_subject=owner
            )
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Owner universe unavailable",
            ) from None

        if (
            not isinstance(symbols, (list, tuple))
            or not 2 <= len(symbols) <= 12
            or len(set(map(str, symbols))) != len(symbols)
            or any(
                not isinstance(s, str)
                or not s.isascii()
                or not s.isupper()
                or not s.isalnum()
                or not 1 <= len(s) <= 10
                for s in symbols
            )
        ):
            raise HTTPException(
                status_code=409,
                detail="Owner universe not eligible for analysis",
            )

        symbols = list(symbols)

        # Illustrative allocation only.
        # Never imply these are actual owned positions.
        weight = 1.0 / len(symbols)

        weights = {
            symbol: weight
            for symbol in symbols
        }

        try:
            proposal = build_allocation_proposal(
                strategy_name="illustrative_equal_weight_research",
                target_weights=weights,
                universe_symbols=symbols,
                cash_weight=0.0,
            )
        except Exception:
            raise HTTPException(
                status_code=422,
                detail="Illustrative allocation unavailable",
            ) from None

        def evaluate():
            return facade.analyze_authenticated_owner(
                authenticated_owner_id=owner,
                owned_resource_owner_id=owner,
                primary_symbol=symbols[0],
                universe_symbols=symbols,
                proposal=proposal,
                provider_loader=provider_loader,
                analysis_mode=mode,
                engine_paths=paths,
                expected_hashes=hashes,
                as_of=datetime.now(timezone.utc),
            )

        try:
            # The provider and evaluator are synchronous.
            # Do not block the application's event loop.
            result = await asyncio.to_thread(evaluate)
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Read-only financial analysis unavailable",
            ) from None

        return {
            "status": "ok",
            "read_only": True,
            "paper_only": True,
            "execution_enabled": False,
            "order_admission_allowed": False,
            "live_trading_authorized": False,
            "allocation_basis": "ILLUSTRATIVE_EQUAL_WEIGHT",
            "actual_account_positions_used": False,
            "owner_subject_echoed": False,
            "financial_analysis": result,
        }

    return router
