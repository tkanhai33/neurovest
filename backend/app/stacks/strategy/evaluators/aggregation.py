"""Pure deterministic aggregation for qualified strategy decisions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from types import MappingProxyType


SMA_STRATEGY_NAME = (
    "Simple Moving Average Crossover"
)

OFFLINE_FAMILY_NAMES = (
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
)

QUALIFIED_AGGREGATION_NAMES = (
    SMA_STRATEGY_NAME,
    *OFFLINE_FAMILY_NAMES,
)

SECOND_OFFLINE_FAMILY_NAMES = (
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)

BULK_OFFLINE_FAMILY_NAMES = (
    "MACD Crossover",
    "MACD Zero-Line",
    "MACD Histogram Momentum",
    "Stochastic Momentum",
    "Stochastic Oversold Reversion",
    "Commodity Channel Index Momentum",
    "CCI Mean Reversion",
    "Rate of Change Momentum",
    "ROC Zero Cross",
    "Time-Series Momentum",
    "RSI Momentum",
    "TRIX Trend",
    "Golden Cross",
    "Exponential Moving Average Crossover",
    "Price Above Moving Average",
)

SECOND_BULK_OFFLINE_FAMILY_NAMES = (
    "Stochastic Pullback in Trend",
    "High-Low Momentum",
    "Price Acceleration",
    "ADX Breakout",
    "ADX Trend Following",
    "DMI Crossover",
    "Hull Moving Average Trend",
    "Moving Average Ribbon",
    "Envelope Mean Reversion",
    "Moving Average Deviation Reversion",
    "Moving Average Crossover with ATR Filter",
    "Moving Average Slope",
    "Triple Moving Average Trend",
    "ATR Compression Expansion",
    "Money Flow Index Reversion",
)

THIRD_BULK_OFFLINE_FAMILY_NAMES = (
    "Parabolic SAR Trend",
    "Aroon Trend",
    "Ichimoku Trend",
    "Supertrend",
    "N-Day High Breakout",
    "N-Day Low Breakdown",
    "NR4 Breakout",
    "NR7 Breakout",
    "Inside Bar Breakout",
    "Triangle Breakout",
    "Z-Score Mean Reversion",
    "Williams %R Reversion",
    "Gap Fade",
    "Overnight Reversal",
    "Short-Term Reversal Factor",
)

COMPATIBLE_AGGREGATION_NAMES = (
    *QUALIFIED_AGGREGATION_NAMES,
    *SECOND_OFFLINE_FAMILY_NAMES,
    *BULK_OFFLINE_FAMILY_NAMES,
    *SECOND_BULK_OFFLINE_FAMILY_NAMES,
    *THIRD_BULK_OFFLINE_FAMILY_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    COMPATIBLE_AGGREGATION_NAMES
)

DIRECTIONAL_DECISIONS = frozenset(
    (
        "BUY",
        "SELL",
    )
)

VALID_DECISIONS = frozenset(
    (
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    )
)

VOTE_VALUES = MappingProxyType(
    {
        "BUY": 1,
        "SELL": -1,
        "HOLD": 0,
    }
)


class StrategyAggregationInputError(ValueError):
    """Evaluator results violate the deterministic aggregation contract."""


def _fail_closed(
    reason: str,
    *,
    error: str | None = None,
    received_results: int = 0,
) -> dict[str, object]:
    result: dict[str, object] = {
        "status": "abstain",
        "provider": "qualified_strategy_aggregation",
        "evaluator_id": "deterministic_strategy_aggregation_v1",
        "decision": "ABSTAIN",
        "signal": "ABSTAIN",
        "confidence": 0.0,
        "reason": reason,
        "received_results": received_results,
        "eligible_results": 0,
        "abstaining_results": 0,
        "buy_votes": 0,
        "sell_votes": 0,
        "hold_votes": 0,
        "net_vote": 0,
        "contributing_strategies": [],
        "abstaining_strategies": [],
        "strategy_results": [],
        "execution_enabled": False,
    }

    if error:
        result["error"] = error

    return result


def _normalized_confidence(
    value: object,
    *,
    index: int,
) -> float:
    if isinstance(
        value,
        bool,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].confidence must be numeric"
        )

    try:
        confidence = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise StrategyAggregationInputError(
            f"results[{index}].confidence must be numeric"
        ) from exc

    if not isfinite(
        confidence
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].confidence must be finite"
        )

    if (
        confidence < 0.0
        or
        confidence > 1.0
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].confidence must be between zero and one"
        )

    return confidence


def _normalize_result(
    raw_result: object,
    *,
    index: int,
) -> dict[str, object]:
    if not isinstance(
        raw_result,
        Mapping,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}] must be a mapping"
        )

    raw_name = raw_result.get(
        "strategy_name"
    )

    if not isinstance(
        raw_name,
        str,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].strategy_name must be a string"
        )

    strategy_name = raw_name.strip()

    if strategy_name not in QUALIFIED_AGGREGATION_NAME_SET:
        raise StrategyAggregationInputError(
            "unqualified strategy result: "
            f"{strategy_name or '<empty>'}"
        )

    raw_decision = raw_result.get(
        "decision",
        raw_result.get(
            "signal"
        ),
    )

    if not isinstance(
        raw_decision,
        str,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].decision must be a string"
        )

    decision = (
        raw_decision
        .strip()
        .upper()
    )

    if decision not in VALID_DECISIONS:
        raise StrategyAggregationInputError(
            f"results[{index}].decision is unsupported: {decision}"
        )

    raw_status = raw_result.get(
        "status",
        "ok",
    )

    if not isinstance(
        raw_status,
        str,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].status must be a string"
        )

    status = (
        raw_status
        .strip()
        .lower()
    )

    if status not in (
        "ok",
        "abstain",
        "abstained",
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].status is unsupported: {status}"
        )

    if status == "abstained":
        status = "abstain"

    if (
        status == "abstain"
        and
        decision != "ABSTAIN"
    ):
        raise StrategyAggregationInputError(
            f"results[{index}] has inconsistent abstain status"
        )

    if (
        status == "ok"
        and
        decision == "ABSTAIN"
    ):
        raise StrategyAggregationInputError(
            f"results[{index}] has inconsistent ok status"
        )

    confidence = _normalized_confidence(
        raw_result.get(
            "confidence",
            0.0,
        ),
        index=index,
    )

    if (
        decision == "ABSTAIN"
        and
        confidence != 0.0
    ):
        raise StrategyAggregationInputError(
            f"results[{index}] abstention confidence must be zero"
        )

    reason = raw_result.get(
        "reason",
        "unspecified",
    )

    if not isinstance(
        reason,
        str,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].reason must be a string"
        )

    evaluator_id = raw_result.get(
        "evaluator_id",
        "unavailable",
    )

    if not isinstance(
        evaluator_id,
        str,
    ):
        raise StrategyAggregationInputError(
            f"results[{index}].evaluator_id must be a string"
        )

    return {
        "strategy_name": strategy_name,
        "evaluator_id": evaluator_id.strip() or "unavailable",
        "decision": decision,
        "status": status,
        "confidence": confidence,
        "reason": reason.strip() or "unspecified",
    }


def aggregate_strategy_results(
    results: Sequence[object],
) -> dict[str, object]:
    if isinstance(
        results,
        (
            str,
            bytes,
        ),
    ) or not isinstance(
        results,
        Sequence,
    ):
        return _fail_closed(
            "invalid_evaluator_results",
            error="results must be a sequence",
        )

    received_results = len(
        results
    )

    if received_results == 0:
        return _fail_closed(
            "no_evaluator_results",
            received_results=0,
        )

    try:
        normalized = [
            _normalize_result(
                raw_result,
                index=index,
            )
            for index, raw_result in enumerate(
                results
            )
        ]
    except StrategyAggregationInputError as exc:
        return _fail_closed(
            "invalid_evaluator_results",
            error=str(exc),
            received_results=received_results,
        )

    names = [
        str(
            result[
                "strategy_name"
            ]
        )
        for result in normalized
    ]

    if len(
        names
    ) != len(
        set(
            names
        )
    ):
        return _fail_closed(
            "duplicate_strategy_results",
            error="each strategy may contribute at most one result",
            received_results=received_results,
        )

    eligible = [
        result
        for result in normalized
        if result[
            "decision"
        ] != "ABSTAIN"
    ]

    abstaining = [
        result
        for result in normalized
        if result[
            "decision"
        ] == "ABSTAIN"
    ]

    if not eligible:
        return {
            **_fail_closed(
                "all_evaluators_abstained",
                received_results=received_results,
            ),
            "abstaining_results": len(
                abstaining
            ),
            "abstaining_strategies": [
                result[
                    "strategy_name"
                ]
                for result in abstaining
            ],
            "strategy_results": normalized,
        }

    buy_results = [
        result
        for result in eligible
        if result[
            "decision"
        ] == "BUY"
    ]

    sell_results = [
        result
        for result in eligible
        if result[
            "decision"
        ] == "SELL"
    ]

    hold_results = [
        result
        for result in eligible
        if result[
            "decision"
        ] == "HOLD"
    ]

    buy_votes = len(
        buy_results
    )

    sell_votes = len(
        sell_results
    )

    hold_votes = len(
        hold_results
    )

    net_vote = (
        buy_votes
        -
        sell_votes
    )

    if buy_votes > sell_votes:
        decision = "BUY"
        reason = "buy_vote_majority"
        winning_results = buy_results
        directional_votes = (
            buy_votes
            +
            sell_votes
        )
        winning_votes = buy_votes

    elif sell_votes > buy_votes:
        decision = "SELL"
        reason = "sell_vote_majority"
        winning_results = sell_results
        directional_votes = (
            buy_votes
            +
            sell_votes
        )
        winning_votes = sell_votes

    elif (
        buy_votes > 0
        and
        sell_votes > 0
    ):
        decision = "HOLD"
        reason = "directional_vote_tie"
        winning_results = []
        directional_votes = (
            buy_votes
            +
            sell_votes
        )
        winning_votes = 0

    else:
        decision = "HOLD"
        reason = "no_directional_vote"
        winning_results = []
        directional_votes = 0
        winning_votes = 0

    if decision in DIRECTIONAL_DECISIONS:
        mean_winner_confidence = (
            sum(
                float(
                    result[
                        "confidence"
                    ]
                )
                for result in winning_results
            )
            /
            len(
                winning_results
            )
        )

        consensus_ratio = (
            winning_votes
            /
            max(
                directional_votes,
                1,
            )
        )

        participation_ratio = (
            directional_votes
            /
            len(
                eligible
            )
        )

        confidence = (
            mean_winner_confidence
            *
            consensus_ratio
            *
            participation_ratio
        )
    else:
        mean_winner_confidence = 0.0
        consensus_ratio = 0.0
        participation_ratio = (
            directional_votes
            /
            len(
                eligible
            )
        )
        confidence = 0.0

    confidence = min(
        max(
            confidence,
            0.0,
        ),
        1.0,
    )

    return {
        "status": "ok",
        "provider": "qualified_strategy_aggregation",
        "evaluator_id": "deterministic_strategy_aggregation_v1",
        "decision": decision,
        "signal": decision,
        "confidence": confidence,
        "reason": reason,
        "received_results": received_results,
        "eligible_results": len(
            eligible
        ),
        "abstaining_results": len(
            abstaining
        ),
        "buy_votes": buy_votes,
        "sell_votes": sell_votes,
        "hold_votes": hold_votes,
        "net_vote": net_vote,
        "directional_votes": directional_votes,
        "winning_votes": winning_votes,
        "mean_winner_confidence": mean_winner_confidence,
        "consensus_ratio": consensus_ratio,
        "participation_ratio": participation_ratio,
        "contributing_strategies": [
            result[
                "strategy_name"
            ]
            for result in eligible
        ],
        "abstaining_strategies": [
            result[
                "strategy_name"
            ]
            for result in abstaining
        ],
        "strategy_results": normalized,
        "execution_enabled": False,
    }


def healthcheck() -> dict[str, object]:
    return {
        "component": "deterministic_strategy_aggregation_v1",
        "healthy": True,
        "qualified_input_names": QUALIFIED_AGGREGATION_NAMES,
        "compatible_input_names": COMPATIBLE_AGGREGATION_NAMES,
        "compatible_input_count": len(
            COMPATIBLE_AGGREGATION_NAMES
        ),
        "second_family_compatible": True,
        "aggregation_policy": "equal_directional_vote_majority",
        "hold_vote_directional_weight": 0,
        "abstentions_excluded": True,
        "duplicates_fail_closed": True,
        "unknown_strategies_fail_closed": True,
        "malformed_results_fail_closed": True,
        "active_registry_modified": False,
        "owner_decision_integrated": False,
        "provider_called": False,
        "database_accessed": False,
        "execution_enabled": False,
    }


# Qualified fourth batch: extend the existing 54-name identity set.
# Do not alter QUALIFIED_AGGREGATION_NAMES, the legacy five-name contract.
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)

QUALIFIED_V4_ACTIVATION_NAMES = tuple(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (
        *QUALIFIED_AGGREGATION_NAME_SET,
        *QUALIFIED_V4_ACTIVATION_NAMES,
    )
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    FIFTH_FIFTEEN_OHLCV_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (
        *QUALIFIED_AGGREGATION_NAME_SET,
        *FIFTH_FIFTEEN_OHLCV_NAMES,
    )
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v6 import (
    SIXTH_FIFTEEN_OHLCV_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (
        *QUALIFIED_AGGREGATION_NAME_SET,
        *SIXTH_FIFTEEN_OHLCV_NAMES,
    )
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v7 import (
    SEVENTH_FIFTEEN_OHLCV_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (
        *QUALIFIED_AGGREGATION_NAME_SET,
        *SEVENTH_FIFTEEN_OHLCV_NAMES,
    )
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v8 import (
    EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (
        *QUALIFIED_AGGREGATION_NAME_SET,
        *EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES,
    )
)


from backend.app.stacks.strategy.evaluators.multi_symbol_family_v1 import (
    MULTI_SYMBOL_STRATEGY_NAMES,
)

QUALIFIED_AGGREGATION_NAME_SET = frozenset(
    (*QUALIFIED_AGGREGATION_NAME_SET, *MULTI_SYMBOL_STRATEGY_NAMES)
)
