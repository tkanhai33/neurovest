"""Isolated qualified aggregation for the offline fourth V4 batch only."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)

VALID_DECISIONS = frozenset(("BUY", "SELL", "HOLD", "ABSTAIN"))
DIRECTIONAL_DECISIONS = frozenset(("BUY", "SELL"))

QUALIFIED_V4_AGGREGATION_NAME_SET = frozenset(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)


class V4StrategyAggregationInputError(ValueError):
    """Raised only within the isolated V4 aggregation boundary."""


def _fail_closed(
    reason: str,
    *,
    error: str | None = None,
    received_results: int = 0,
) -> dict[str, object]:
    output: dict[str, object] = {
        "status": "abstain",
        "provider": "qualified_strategy_aggregation_v4_offline",
        "evaluator_id": "deterministic_strategy_aggregation_v4",
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
        "directional_votes": 0,
        "winning_votes": 0,
        "mean_winner_confidence": 0.0,
        "consensus_ratio": 0.0,
        "participation_ratio": 0.0,
        "contributing_strategies": [],
        "abstaining_strategies": [],
        "strategy_results": [],
        "execution_enabled": False,
    }

    if error is not None:
        output["error"] = error

    return output


def _normalized_confidence(
    value: object,
    *,
    index: int,
) -> float:
    if isinstance(value, bool):
        raise V4StrategyAggregationInputError(
            f"results[{index}].confidence must be numeric"
        )

    try:
        confidence = float(value)
    except (TypeError, ValueError) as exc:
        raise V4StrategyAggregationInputError(
            f"results[{index}].confidence must be numeric"
        ) from exc

    if not isfinite(confidence):
        raise V4StrategyAggregationInputError(
            f"results[{index}].confidence must be finite"
        )

    if confidence < 0.0 or confidence > 1.0:
        raise V4StrategyAggregationInputError(
            f"results[{index}].confidence must be between zero and one"
        )

    return confidence


def _normalize_result(
    raw_result: object,
    *,
    index: int,
) -> dict[str, object]:
    if not isinstance(raw_result, Mapping):
        raise V4StrategyAggregationInputError(
            f"results[{index}] must be a mapping"
        )

    raw_name = raw_result.get("strategy_name")

    if not isinstance(raw_name, str):
        raise V4StrategyAggregationInputError(
            f"results[{index}].strategy_name must be a string"
        )

    strategy_name = raw_name.strip()

    if strategy_name not in QUALIFIED_V4_AGGREGATION_NAME_SET:
        raise V4StrategyAggregationInputError(
            "unqualified V4 strategy result: "
            f"{strategy_name or '<empty>'}"
        )

    raw_decision = raw_result.get(
        "decision",
        raw_result.get("signal"),
    )

    if not isinstance(raw_decision, str):
        raise V4StrategyAggregationInputError(
            f"results[{index}].decision must be a string"
        )

    decision = raw_decision.strip().upper()

    if decision not in VALID_DECISIONS:
        raise V4StrategyAggregationInputError(
            f"results[{index}].decision is unsupported: {decision}"
        )

    raw_status = raw_result.get("status", "ok")

    if not isinstance(raw_status, str):
        raise V4StrategyAggregationInputError(
            f"results[{index}].status must be a string"
        )

    status = raw_status.strip().lower()

    if status not in ("ok", "abstain", "abstained"):
        raise V4StrategyAggregationInputError(
            f"results[{index}].status is unsupported: {status}"
        )

    if status == "abstained":
        status = "abstain"

    if status == "abstain" and decision != "ABSTAIN":
        raise V4StrategyAggregationInputError(
            f"results[{index}] has inconsistent abstain status"
        )

    if status == "ok" and decision == "ABSTAIN":
        raise V4StrategyAggregationInputError(
            f"results[{index}] has inconsistent ok status"
        )

    confidence = _normalized_confidence(
        raw_result.get("confidence", 0.0),
        index=index,
    )

    if decision == "ABSTAIN" and confidence != 0.0:
        raise V4StrategyAggregationInputError(
            f"results[{index}] abstention confidence must be zero"
        )

    reason = raw_result.get("reason", "unspecified")
    evaluator_id = raw_result.get("evaluator_id", "unavailable")

    if not isinstance(reason, str):
        raise V4StrategyAggregationInputError(
            f"results[{index}].reason must be a string"
        )

    if not isinstance(evaluator_id, str):
        raise V4StrategyAggregationInputError(
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


def aggregate_v4_strategy_results(
    results: Sequence[object],
) -> dict[str, object]:
    """Apply the qualified aggregation policy to the exact V4 identity set."""

    if isinstance(results, (str, bytes)) or not isinstance(results, Sequence):
        return _fail_closed(
            "invalid_evaluator_results",
            error="results must be a sequence",
        )

    received_results = len(results)

    if received_results == 0:
        return _fail_closed(
            "no_evaluator_results",
            received_results=0,
        )

    try:
        normalized = [
            _normalize_result(raw_result, index=index)
            for index, raw_result in enumerate(results)
        ]
    except V4StrategyAggregationInputError as exc:
        return _fail_closed(
            "invalid_evaluator_results",
            error=str(exc),
            received_results=received_results,
        )

    names = [str(result["strategy_name"]) for result in normalized]

    if len(names) != len(set(names)):
        return _fail_closed(
            "duplicate_strategy_results",
            error="each strategy may contribute at most one result",
            received_results=received_results,
        )

    eligible = [
        result for result in normalized
        if result["decision"] != "ABSTAIN"
    ]
    abstaining = [
        result for result in normalized
        if result["decision"] == "ABSTAIN"
    ]

    if not eligible:
        return {
            **_fail_closed(
                "all_evaluators_abstained",
                received_results=received_results,
            ),
            "abstaining_results": len(abstaining),
            "abstaining_strategies": [
                result["strategy_name"]
                for result in abstaining
            ],
            "strategy_results": normalized,
        }

    buy_results = [
        result for result in eligible
        if result["decision"] == "BUY"
    ]
    sell_results = [
        result for result in eligible
        if result["decision"] == "SELL"
    ]
    hold_results = [
        result for result in eligible
        if result["decision"] == "HOLD"
    ]

    buy_votes = len(buy_results)
    sell_votes = len(sell_results)
    hold_votes = len(hold_results)
    net_vote = buy_votes - sell_votes

    if buy_votes > sell_votes:
        decision = "BUY"
        reason = "buy_vote_majority"
        winning_results = buy_results
        directional_votes = buy_votes + sell_votes
        winning_votes = buy_votes
    elif sell_votes > buy_votes:
        decision = "SELL"
        reason = "sell_vote_majority"
        winning_results = sell_results
        directional_votes = buy_votes + sell_votes
        winning_votes = sell_votes
    elif buy_votes > 0 and sell_votes > 0:
        decision = "HOLD"
        reason = "directional_vote_tie"
        winning_results = []
        directional_votes = buy_votes + sell_votes
        winning_votes = 0
    else:
        decision = "HOLD"
        reason = "no_directional_vote"
        winning_results = []
        directional_votes = 0
        winning_votes = 0

    if decision in DIRECTIONAL_DECISIONS:
        mean_winner_confidence = (
            sum(float(result["confidence"]) for result in winning_results)
            / len(winning_results)
        )
        consensus_ratio = winning_votes / max(directional_votes, 1)
        participation_ratio = directional_votes / len(eligible)
        confidence = (
            mean_winner_confidence
            * consensus_ratio
            * participation_ratio
        )
    else:
        mean_winner_confidence = 0.0
        consensus_ratio = 0.0
        participation_ratio = directional_votes / len(eligible)
        confidence = 0.0

    confidence = min(max(confidence, 0.0), 1.0)

    return {
        "status": "ok",
        "provider": "qualified_strategy_aggregation_v4_offline",
        "evaluator_id": "deterministic_strategy_aggregation_v4",
        "decision": decision,
        "signal": decision,
        "confidence": confidence,
        "reason": reason,
        "received_results": received_results,
        "eligible_results": len(eligible),
        "abstaining_results": len(abstaining),
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
            result["strategy_name"]
            for result in eligible
        ],
        "abstaining_strategies": [
            result["strategy_name"]
            for result in abstaining
        ],
        "strategy_results": normalized,
        "execution_enabled": False,
    }


def evaluate_and_aggregate_v4(
    bars: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """Evaluate the isolated fifteen V4 strategies then aggregate offline."""

    return aggregate_v4_strategy_results(
        tuple(
            evaluator(bars)
            for evaluator in BULK_OFFLINE_EVALUATORS_V4.values()
        )
    )


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": len(QUALIFIED_V4_AGGREGATION_NAME_SET),
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
