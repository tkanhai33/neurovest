"""Validated, non-executable portfolio allocation proposals."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import isclose, isfinite

WEIGHT_TOLERANCE = 1e-9


class AllocationProposalError(ValueError):
    """Raised when an allocation proposal is malformed or unsafe."""


def _symbols(values: Iterable[object]) -> tuple[str, ...]:
    cleaned: list[str] = []

    for value in values:
        symbol = str(value).strip().upper()
        if not symbol or symbol in cleaned:
            raise AllocationProposalError(
                "universe symbols must be non-empty and unique"
            )
        cleaned.append(symbol)

    if len(cleaned) < 2:
        raise AllocationProposalError(
            "allocation proposals require at least two universe symbols"
        )

    return tuple(cleaned)


def build_allocation_proposal(
    *,
    strategy_name: object,
    target_weights: Mapping[object, object],
    universe_symbols: Iterable[object],
    cash_weight: object = 0.0,
) -> dict[str, object]:
    """Return a validated target-weight proposal; never an execution instruction."""

    name = str(strategy_name).strip()
    universe = _symbols(universe_symbols)

    if not name:
        raise AllocationProposalError("strategy_name must not be empty")

    if not isinstance(target_weights, Mapping):
        raise AllocationProposalError("target_weights must be a mapping")

    weights: dict[str, float] = {}

    for raw_symbol, raw_weight in target_weights.items():
        symbol = str(raw_symbol).strip().upper()

        if symbol not in universe:
            raise AllocationProposalError(
                f"target symbol is outside the owner universe: {symbol}"
            )

        if symbol in weights:
            raise AllocationProposalError(
                f"duplicate target symbol: {symbol}"
            )

        try:
            weight = float(raw_weight)
        except (TypeError, ValueError) as exc:
            raise AllocationProposalError(
                f"invalid target weight for {symbol}"
            ) from exc

        if not isfinite(weight) or weight < 0.0:
            raise AllocationProposalError(
                f"target weight must be finite and non-negative: {symbol}"
            )

        weights[symbol] = weight

    try:
        cash = float(cash_weight)
    except (TypeError, ValueError) as exc:
        raise AllocationProposalError("invalid cash_weight") from exc

    if not isfinite(cash) or cash < 0.0 or cash > 1.0:
        raise AllocationProposalError(
            "cash_weight must be finite and within [0.0, 1.0]"
        )

    total = sum(weights.values()) + cash

    if not weights and not isclose(
        cash,
        1.0,
        abs_tol=WEIGHT_TOLERANCE,
    ):
        raise AllocationProposalError(
            "an empty target mapping requires cash_weight equal to 1.0"
        )

    if not isclose(total, 1.0, abs_tol=WEIGHT_TOLERANCE):
        raise AllocationProposalError(
            f"target weights plus cash_weight must equal 1.0, got {total}"
        )

    return {
        "status": "ok",
        "proposal_type": "target_weights",
        "strategy_name": name,
        "universe_symbols": list(universe),
        "target_weights": dict(sorted(weights.items())),
        "cash_weight": cash,
        "rebalance_action": "proposal_only",
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }
