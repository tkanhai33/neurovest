"""Pure deterministic Simple Moving Average Crossover evaluator."""

from __future__ import annotations

from math import isfinite
from typing import Any, Sequence


STRATEGY_NAME = "Simple Moving Average Crossover"
EVALUATOR_ID = "simple_moving_average_crossover_v1"

SHORT_WINDOW = 5
LONG_WINDOW = 20
MINIMUM_BARS = LONG_WINDOW + 1


class SmaCrossoverInputError(ValueError):
    """Replay input violates the evaluator's deterministic contract."""


def _finite_close(
    bar: object,
    *,
    index: int,
) -> float:
    if not isinstance(
        bar,
        dict,
    ):
        raise SmaCrossoverInputError(
            f"bar {index} must be a mapping"
        )

    if "close" not in bar:
        raise SmaCrossoverInputError(
            f"bar {index} is missing close"
        )

    value = bar[
        "close"
    ]

    if isinstance(
        value,
        bool,
    ):
        raise SmaCrossoverInputError(
            f"bar {index} close must be numeric"
        )

    try:
        close = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SmaCrossoverInputError(
            f"bar {index} close must be numeric"
        ) from exc

    if not isfinite(
        close
    ):
        raise SmaCrossoverInputError(
            f"bar {index} close must be finite"
        )

    if close <= 0.0:
        raise SmaCrossoverInputError(
            f"bar {index} close must be greater than zero"
        )

    return close


def _mean(
    values: Sequence[float],
) -> float:
    return sum(
        values
    ) / len(
        values
    )


def _abstention(
    *,
    received_bars: int,
    reason: str,
) -> dict[str, Any]:
    return {
        "status": "abstained",
        "strategy_name": STRATEGY_NAME,
        "evaluator_id": EVALUATOR_ID,
        "decision": "ABSTAIN",
        "signal": "hold",
        "confidence": 0.0,
        "reason": reason,
        "short_window": SHORT_WINDOW,
        "long_window": LONG_WINDOW,
        "minimum_bars": MINIMUM_BARS,
        "received_bars": received_bars,
    }


def evaluate_sma_crossover(
    bars: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate a 5/20 SMA crossover using only supplied replay bars.

    BUY requires the fast average to cross from at-or-below the slow
    average to above it on the newest bar. SELL requires the inverse
    transition. An established non-crossing relationship returns HOLD.
    """

    if isinstance(
        bars,
        (
            str,
            bytes,
        ),
    ) or not isinstance(
        bars,
        Sequence,
    ):
        raise SmaCrossoverInputError(
            "bars must be a sequence"
        )

    received_bars = len(
        bars
    )

    if received_bars < MINIMUM_BARS:
        return _abstention(
            received_bars=received_bars,
            reason="insufficient_truthful_bars",
        )

    closes = [
        _finite_close(
            bar,
            index=index,
        )
        for index, bar in enumerate(
            bars
        )
    ]

    previous = closes[:-1]

    previous_fast = _mean(
        previous[
            -SHORT_WINDOW:
        ]
    )

    previous_slow = _mean(
        previous[
            -LONG_WINDOW:
        ]
    )

    current_fast = _mean(
        closes[
            -SHORT_WINDOW:
        ]
    )

    current_slow = _mean(
        closes[
            -LONG_WINDOW:
        ]
    )

    crossed_above = (
        previous_fast
        <= previous_slow
        and
        current_fast
        > current_slow
    )

    crossed_below = (
        previous_fast
        >= previous_slow
        and
        current_fast
        < current_slow
    )

    if crossed_above:
        decision = "BUY"
        signal = "buy"
        reason = "fast_sma_crossed_above_slow_sma"

    elif crossed_below:
        decision = "SELL"
        signal = "sell"
        reason = "fast_sma_crossed_below_slow_sma"

    else:
        decision = "HOLD"
        signal = "hold"
        reason = "no_new_sma_crossover"

    denominator = max(
        abs(
            current_slow
        ),
        1e-12,
    )

    separation = abs(
        current_fast
        -
        current_slow
    ) / denominator

    confidence = min(
        1.0,
        round(
            separation,
            12,
        ),
    )

    return {
        "status": "ok",
        "strategy_name": STRATEGY_NAME,
        "evaluator_id": EVALUATOR_ID,
        "decision": decision,
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "short_window": SHORT_WINDOW,
        "long_window": LONG_WINDOW,
        "minimum_bars": MINIMUM_BARS,
        "received_bars": received_bars,
        "previous_fast_sma": previous_fast,
        "previous_slow_sma": previous_slow,
        "current_fast_sma": current_fast,
        "current_slow_sma": current_slow,
    }


def healthcheck() -> dict[str, object]:
    """Describe the pure evaluator without reading data or services."""

    return {
        "component": EVALUATOR_ID,
        "healthy": True,
        "strategy_name": STRATEGY_NAME,
        "short_window": SHORT_WINDOW,
        "long_window": LONG_WINDOW,
        "minimum_bars": MINIMUM_BARS,
        "pure_replay_only": True,
        "provider_called": False,
        "database_accessed": False,
        "execution_enabled": False,
    }
