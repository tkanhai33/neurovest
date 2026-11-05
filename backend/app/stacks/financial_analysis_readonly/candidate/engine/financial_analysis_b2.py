"""Isolated B2 financial analysis qualification.

Historical simulation only. No database, network, or broker access.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class FinancialIntegrityError(RuntimeError):
    pass


def _timestamp(value: object) -> str:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise FinancialIntegrityError(
                "invalid_timestamp"
            ) from exc
    else:
        raise FinancialIntegrityError("invalid_timestamp")

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FinancialIntegrityError("naive_timestamp")

    return parsed.astimezone(timezone.utc).isoformat()


def _canonical(value: object) -> Any:
    if isinstance(value, datetime):
        return _timestamp(value)

    if isinstance(value, Mapping):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise FinancialIntegrityError(
                    "nonstring_mapping_key"
                )
            result[key] = _canonical(item)
        return result

    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]

    if isinstance(value, bool) or value is None:
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise FinancialIntegrityError(
                "nonfinite_evidence_value"
            )
        return value

    if isinstance(value, str):
        return value

    raise FinancialIntegrityError(
        "unsupported_evidence_type"
    )


def _fingerprint(value: object) -> str:
    encoded = json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def _load_b1(candidate: Path):
    if not candidate.is_file() or candidate.is_symlink():
        raise FinancialIntegrityError("b1_candidate_missing")

    spec = importlib.util.spec_from_file_location(
        "neuro_financial_integrity_b1",
        candidate,
    )

    if spec is None or spec.loader is None:
        raise FinancialIntegrityError("b1_loader_unavailable")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(
    *,
    primary_symbol: str,
    universe_bars: object,
    proposal: object,
    b1_candidate: Path,
    rebalance_interval_bars: int = 21,
    transaction_cost_bps: float = 10.0,
) -> dict[str, Any]:

    # Never mutate caller-owned evidence.
    raw = deepcopy(universe_bars)

    if not isinstance(raw, dict) or not raw:
        raise FinancialIntegrityError("universe_invalid")

    dates = []

    for symbol, bars in raw.items():
        if not isinstance(bars, (list, tuple)):
            raise FinancialIntegrityError("history_invalid")

        observed = []

        for bar in bars:
            if not isinstance(bar, dict):
                raise FinancialIntegrityError("bar_invalid")

            timestamp = _timestamp(bar.get("timestamp"))
            observed.append(timestamp)
            bar["timestamp"] = timestamp

        if observed != sorted(observed):
            raise FinancialIntegrityError(
                "history_not_chronological"
            )

        if len(observed) != len(set(observed)):
            raise FinancialIntegrityError(
                "duplicate_observation"
            )

        dates.append(tuple(observed))

    # B2 requires identical timestamps, not just an overlapping
    # subset. Prevents silently comparing different sessions.
    if len(set(dates)) != 1:
        raise FinancialIntegrityError(
            "unaligned_portfolio_history"
        )

    from backend.app.stacks.strategy.allocation_paper_evaluation import (
        _canonical_proposal,
    )

    canonical_proposal = _canonical_proposal(proposal)

    weights = canonical_proposal.get("target_weights")

    if not isinstance(weights, dict):
        raise FinancialIntegrityError(
            "proposal_weights_invalid"
        )

    if not set(weights).issubset(set(raw)):
        raise FinancialIntegrityError(
            "proposal_universe_mismatch"
        )

    b1 = _load_b1(b1_candidate)

    result = b1.evaluate_financial_intelligence(
        primary_symbol=primary_symbol,
        universe_bars=raw,
        proposal=canonical_proposal,
        rebalance_interval_bars=rebalance_interval_bars,
        transaction_cost_bps=transaction_cost_bps,
    )

    if (
        result.get("actual_v4_evaluator_count") != 15
        or result.get("execution_enabled") is not False
        or result.get("broker_order_generation_enabled") is not False
        or result.get("live_trading_authorized") is not False
    ):
        raise FinancialIntegrityError(
            "underlying_analysis_contract_invalid"
        )

    evidence_hash = _fingerprint({
        "primary_symbol": primary_symbol,
        "universe_bars": raw,
        "proposal": canonical_proposal,
        "rebalance_interval_bars": rebalance_interval_bars,
        "transaction_cost_bps": transaction_cost_bps,
    })

    result["analysis_evidence_sha256"] = evidence_hash
    result["proposal_bound_to_evidence"] = True
    result["portfolio_timestamps_aligned"] = True
    result["data_origin"] = "DETERMINISTIC_FIXTURE"
    result["risk_assessment_kind"] = (
        "HISTORICAL_ANALYSIS_ONLY"
    )
    result["final_execution_risk_gate_passed"] = False
    result["order_admission_allowed"] = False
    result["broker_order_generation_enabled"] = False
    result["execution_enabled"] = False
    result["live_trading_authorized"] = False

    return result
