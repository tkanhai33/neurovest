"""NeuroVest: isolated financial analysis candidate.

Static historical-data evaluation only.
No database access, provider network calls, or order execution.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from typing import Any, Mapping


class FinancialAnalysisUnavailable(RuntimeError):
    pass


def _verify_history(
    universe_bars: object,
    primary_symbol: str,
) -> tuple[dict[str, list[dict[str, Any]]], str]:

    if not isinstance(universe_bars, dict):
        raise FinancialAnalysisUnavailable(
            "universe_must_be_mapping"
        )

    if not 2 <= len(universe_bars) <= 12:
        raise FinancialAnalysisUnavailable(
            "universe_size_outside_limits"
        )

    verified = {}

    for symbol, raw_bars in universe_bars.items():
        if (
            not isinstance(symbol, str)
            or not symbol
            or symbol != symbol.strip().upper()
            or len(symbol) > 20
        ):
            raise FinancialAnalysisUnavailable(
                "invalid_universe_symbol"
            )

        if not isinstance(raw_bars, (list, tuple)):
            raise FinancialAnalysisUnavailable(
                "history_must_be_sequence"
            )

        if len(raw_bars) < 253:
            raise FinancialAnalysisUnavailable(
                "insufficient_history"
            )

        normalized = []
        timestamps = set()

        for raw in raw_bars:
            if not isinstance(raw, Mapping):
                raise FinancialAnalysisUnavailable(
                    "invalid_bar_record"
                )

            bar = dict(raw)

            try:
                values = {
                    field: float(bar[field])
                    for field in (
                        "open", "high", "low", "close"
                    )
                }
            except (KeyError, TypeError, ValueError):
                raise FinancialAnalysisUnavailable(
                    "invalid_ohlc"
                ) from None

            if not all(
                math.isfinite(value) and value > 0
                for value in values.values()
            ):
                raise FinancialAnalysisUnavailable(
                    "nonfinite_or_nonpositive_price"
                )

            if (
                values["high"] < max(
                    values["open"], values["close"]
                )
                or values["low"] > min(
                    values["open"], values["close"]
                )
                or values["low"] > values["high"]
            ):
                raise FinancialAnalysisUnavailable(
                    "inconsistent_ohlc"
                )

            timestamp = bar.get("timestamp")

            if isinstance(timestamp, datetime):
                if timestamp.tzinfo is None:
                    raise FinancialAnalysisUnavailable(
                        "naive_timestamp"
                    )
                key = timestamp.isoformat()
            elif isinstance(timestamp, str):
                try:
                    parsed = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                except ValueError:
                    raise FinancialAnalysisUnavailable(
                        "invalid_timestamp"
                    ) from None

                if parsed.tzinfo is None:
                    raise FinancialAnalysisUnavailable(
                        "naive_timestamp"
                    )

                key = parsed.isoformat()
            else:
                raise FinancialAnalysisUnavailable(
                    "invalid_timestamp"
                )

            if key in timestamps:
                raise FinancialAnalysisUnavailable(
                    "duplicate_timestamp"
                )

            timestamps.add(key)
            normalized.append((key, bar))

        normalized.sort(key=lambda pair: pair[0])
        verified[symbol] = [
            bar for _, bar in normalized
        ]

    primary = str(primary_symbol).strip().upper()

    if primary not in verified:
        raise FinancialAnalysisUnavailable(
            "primary_symbol_not_in_universe"
        )

    date_sets = [
        {
            (
                b["timestamp"].isoformat()
                if isinstance(b["timestamp"], datetime)
                else datetime.fromisoformat(
                    b["timestamp"].replace("Z", "+00:00")
                ).isoformat()
            )
            for b in bars
        }
        for bars in verified.values()
    ]

    if len(set.intersection(*date_sets)) < 253:
        raise FinancialAnalysisUnavailable(
            "insufficient_shared_history"
        )

    return verified, primary


def evaluate_financial_intelligence(
    *,
    primary_symbol: str,
    universe_bars: object,
    proposal: object,
    rebalance_interval_bars: int = 21,
    transaction_cost_bps: float = 10.0,
) -> dict[str, Any]:
    """Run genuine offline implementations; never place orders."""

    verified, primary = _verify_history(
        universe_bars, primary_symbol
    )

    if (
        isinstance(rebalance_interval_bars, bool)
        or not isinstance(rebalance_interval_bars, int)
        or rebalance_interval_bars < 1
    ):
        raise FinancialAnalysisUnavailable(
            "invalid_rebalance_interval"
        )

    try:
        cost = float(transaction_cost_bps)
    except (ValueError, TypeError):
        raise FinancialAnalysisUnavailable(
            "invalid_transaction_cost"
        ) from None

    if not math.isfinite(cost) or cost < 0:
        raise FinancialAnalysisUnavailable(
            "invalid_transaction_cost"
        )

    from backend.app.stacks.strategy.evaluators.bulk_indicator_aggregation_adapter_v4 import (
        evaluate_bulk_indicator_batch_v4,
    )
    from backend.app.stacks.strategy.evaluators.aggregation import (
        aggregate_strategy_results,
    )
    from backend.app.stacks.strategy.allocation_paper_evaluation import (
        evaluate_fixed_weight_proposal_snapshot,
    )

    # Actual fifteen evaluator results, not replacement signals.
    decisions = evaluate_bulk_indicator_batch_v4(
        verified[primary]
    )

    if len(decisions) != 15:
        raise FinancialAnalysisUnavailable(
            "unexpected_v4_evaluator_count"
        )

    aggregation = aggregate_strategy_results(decisions)

    allocation = evaluate_fixed_weight_proposal_snapshot(
        proposal=proposal,
        universe_bars=verified,
        rebalance_interval_bars=rebalance_interval_bars,
        transaction_cost_bps=cost,
    )

    if not isinstance(aggregation, dict):
        raise FinancialAnalysisUnavailable(
            "invalid_aggregation_contract"
        )

    if not isinstance(allocation, dict):
        raise FinancialAnalysisUnavailable(
            "invalid_allocation_contract"
        )

    # Hash a canonical representation of the input evidence,
    # using stable strings for datetime values.
    evidence_bytes = json.dumps(
        {
            "primary_symbol": primary,
            "universe_bars": verified,
            "rebalance_interval_bars":
                rebalance_interval_bars,
            "transaction_cost_bps": cost,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
        allow_nan=False,
    ).encode()

    return {
        "status": "offline_analysis_complete",
        "classification": "HISTORICAL_PAPER_ANALYSIS",
        "primary_symbol": primary,
        "universe_symbols": sorted(verified),
        "history_sha256": hashlib.sha256(
            evidence_bytes
        ).hexdigest(),
        "actual_v4_evaluator_count": len(decisions),
        "strategy_aggregation": aggregation,
        "portfolio_evaluation": allocation,
        "strategy_backtest": False,
        "live_market_data_verified": False,
        "risk_execution_authorized": False,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
        "live_trading_authorized": False,
        "limitations": [
            "Historical fixture data, not verified live prices",
            "Allocation snapshot, not a strategy backtest",
            "No authoritative account equity or ledger state",
            "No final financial policy or order authorization",
        ],
    }
