"""Offline-qualified deterministic Bollinger and RSI evaluators."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from types import MappingProxyType
from typing import Callable

from backend.app.stacks.strategy.evaluators.indicators import (
    IndicatorInputError,
    calculate_bollinger_bands,
    calculate_rsi,
)
from backend.app.stacks.strategy.evaluators.indicator_strategy_contracts import (
    BOLLINGER_BREAKOUT,
    BOLLINGER_MEAN_REVERSION,
    RSI_OVERBOUGHT_MEAN_REVERSION,
    RSI_OVERSOLD_MEAN_REVERSION,
    IndicatorStrategyContract,
)


class IndicatorFamilyInputError(ValueError):
    """Supplied bar data violates the evaluator input contract."""


def _abstain(
    contract: IndicatorStrategyContract,
    *,
    received_bars: int,
    reason: str,
    error: str | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "status": "abstain",
        "strategy_name": contract.strategy_name,
        "evaluator_id": contract.evaluator_id,
        "decision": "ABSTAIN",
        "signal": "ABSTAIN",
        "confidence": 0.0,
        "reason": reason,
        "received_bars": received_bars,
        "minimum_bars": contract.minimum_bars,
        "window": contract.window,
        "transition_only": contract.transition_only,
    }

    if error:
        result["error"] = error

    return result


def _result(
    contract: IndicatorStrategyContract,
    *,
    decision: str,
    confidence: float,
    reason: str,
    received_bars: int,
    evidence: Mapping[str, object],
) -> dict[str, object]:
    bounded_confidence = min(
        max(
            float(confidence),
            0.0,
        ),
        1.0,
    )

    return {
        "status": "ok",
        "strategy_name": contract.strategy_name,
        "evaluator_id": contract.evaluator_id,
        "decision": decision,
        "signal": decision,
        "confidence": bounded_confidence,
        "reason": reason,
        "received_bars": received_bars,
        "minimum_bars": contract.minimum_bars,
        "window": contract.window,
        "transition_only": contract.transition_only,
        **dict(evidence),
    }


def _extract_closes(
    bars: Sequence[object],
) -> list[float]:
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
        raise IndicatorFamilyInputError(
            "bars must be a sequence"
        )

    closes: list[float] = []

    for index, raw_bar in enumerate(
        bars
    ):
        if not isinstance(
            raw_bar,
            Mapping,
        ):
            raise IndicatorFamilyInputError(
                f"bars[{index}] must be a mapping"
            )

        raw_close = raw_bar.get(
            "close"
        )

        if isinstance(
            raw_close,
            bool,
        ):
            raise IndicatorFamilyInputError(
                f"bars[{index}].close must be numeric"
            )

        try:
            close = float(
                raw_close
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise IndicatorFamilyInputError(
                f"bars[{index}].close must be numeric"
            ) from exc

        if (
            not isfinite(close)
            or
            close <= 0.0
        ):
            raise IndicatorFamilyInputError(
                f"bars[{index}].close must be finite and greater than zero"
            )

        closes.append(
            close
        )

    return closes


def _bollinger_values(
    bars: Sequence[object],
    contract: IndicatorStrategyContract,
) -> tuple[
    list[float],
    float,
    float,
    float,
    float,
    float,
    float,
]:
    closes = _extract_closes(
        bars
    )

    if contract.multiplier is None:
        raise IndicatorFamilyInputError(
            "Bollinger multiplier is unavailable"
        )

    bands = calculate_bollinger_bands(
        closes,
        window=contract.window,
        multiplier=contract.multiplier,
    )

    previous_upper = bands[
        "upper"
    ][-2]

    previous_lower = bands[
        "lower"
    ][-2]

    current_upper = bands[
        "upper"
    ][-1]

    current_lower = bands[
        "lower"
    ][-1]

    if any(
        value is None
        for value in (
            previous_upper,
            previous_lower,
            current_upper,
            current_lower,
        )
    ):
        raise IndicatorFamilyInputError(
            "Bollinger values are unavailable after warm-up"
        )

    return (
        closes,
        closes[-2],
        closes[-1],
        float(previous_upper),
        float(previous_lower),
        float(current_upper),
        float(current_lower),
    )


def _bollinger_confidence(
    close: float,
    boundary: float,
) -> float:
    return min(
        abs(
            close
            -
            boundary
        )
        /
        max(
            abs(boundary),
            1e-12,
        ),
        1.0,
    )


def evaluate_bollinger_band_breakout(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = BOLLINGER_BREAKOUT

    try:
        received = len(
            bars
        )
    except TypeError:
        received = 0

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    try:
        (
            _,
            previous_close,
            current_close,
            previous_upper,
            previous_lower,
            current_upper,
            current_lower,
        ) = _bollinger_values(
            bars,
            contract,
        )
    except (
        IndicatorFamilyInputError,
        IndicatorInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(exc),
        )

    if (
        previous_close <= previous_upper
        and
        current_close > current_upper
    ):
        decision = "BUY"
        reason = "close_crossed_above_upper_band"
        confidence = _bollinger_confidence(
            current_close,
            current_upper,
        )

    elif (
        previous_close >= previous_lower
        and
        current_close < current_lower
    ):
        decision = "SELL"
        reason = "close_crossed_below_lower_band"
        confidence = _bollinger_confidence(
            current_close,
            current_lower,
        )

    else:
        decision = "HOLD"
        reason = "no_new_bollinger_breakout"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "multiplier": contract.multiplier,
            "previous_close": previous_close,
            "current_close": current_close,
            "previous_upper_band": previous_upper,
            "previous_lower_band": previous_lower,
            "current_upper_band": current_upper,
            "current_lower_band": current_lower,
        },
    )


def evaluate_bollinger_band_mean_reversion(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = BOLLINGER_MEAN_REVERSION

    try:
        received = len(
            bars
        )
    except TypeError:
        received = 0

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    try:
        (
            _,
            previous_close,
            current_close,
            previous_upper,
            previous_lower,
            current_upper,
            current_lower,
        ) = _bollinger_values(
            bars,
            contract,
        )
    except (
        IndicatorFamilyInputError,
        IndicatorInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(exc),
        )

    if (
        previous_close >= previous_lower
        and
        current_close < current_lower
    ):
        decision = "BUY"
        reason = "close_crossed_below_lower_band"
        confidence = _bollinger_confidence(
            current_close,
            current_lower,
        )

    elif (
        previous_close <= previous_upper
        and
        current_close > current_upper
    ):
        decision = "SELL"
        reason = "close_crossed_above_upper_band"
        confidence = _bollinger_confidence(
            current_close,
            current_upper,
        )

    else:
        decision = "HOLD"
        reason = "no_new_bollinger_mean_reversion_entry"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "multiplier": contract.multiplier,
            "previous_close": previous_close,
            "current_close": current_close,
            "previous_upper_band": previous_upper,
            "previous_lower_band": previous_lower,
            "current_upper_band": current_upper,
            "current_lower_band": current_lower,
        },
    )


def _rsi_values(
    bars: Sequence[object],
    contract: IndicatorStrategyContract,
) -> tuple[
    float,
    float,
]:
    closes = _extract_closes(
        bars
    )

    values = calculate_rsi(
        closes,
        window=contract.window,
    )

    previous_rsi = values[-2]
    current_rsi = values[-1]

    if (
        previous_rsi is None
        or
        current_rsi is None
    ):
        raise IndicatorFamilyInputError(
            "RSI values are unavailable after warm-up"
        )

    return (
        float(previous_rsi),
        float(current_rsi),
    )


def _rsi_confidence(
    value: float,
    threshold: float,
) -> float:
    return min(
        abs(
            value
            -
            threshold
        )
        /
        100.0,
        1.0,
    )


def evaluate_rsi_overbought_mean_reversion(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = RSI_OVERBOUGHT_MEAN_REVERSION

    try:
        received = len(
            bars
        )
    except TypeError:
        received = 0

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    threshold = contract.overbought_threshold

    if threshold is None:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_parameter_contract",
        )

    try:
        previous_rsi, current_rsi = _rsi_values(
            bars,
            contract,
        )
    except (
        IndicatorFamilyInputError,
        IndicatorInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(exc),
        )

    if (
        previous_rsi <= threshold
        and
        current_rsi > threshold
    ):
        decision = "SELL"
        reason = "rsi_crossed_above_overbought_threshold"
        confidence = _rsi_confidence(
            current_rsi,
            threshold,
        )
    else:
        decision = "HOLD"
        reason = "no_new_rsi_overbought_transition"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "previous_rsi": previous_rsi,
            "current_rsi": current_rsi,
            "overbought_threshold": threshold,
            "neutral_threshold": contract.neutral_threshold,
        },
    )


def evaluate_rsi_oversold_mean_reversion(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = RSI_OVERSOLD_MEAN_REVERSION

    try:
        received = len(
            bars
        )
    except TypeError:
        received = 0

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    threshold = contract.oversold_threshold

    if threshold is None:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_parameter_contract",
        )

    try:
        previous_rsi, current_rsi = _rsi_values(
            bars,
            contract,
        )
    except (
        IndicatorFamilyInputError,
        IndicatorInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(exc),
        )

    if (
        previous_rsi >= threshold
        and
        current_rsi < threshold
    ):
        decision = "BUY"
        reason = "rsi_crossed_below_oversold_threshold"
        confidence = _rsi_confidence(
            current_rsi,
            threshold,
        )
    else:
        decision = "HOLD"
        reason = "no_new_rsi_oversold_transition"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "previous_rsi": previous_rsi,
            "current_rsi": current_rsi,
            "oversold_threshold": threshold,
            "neutral_threshold": contract.neutral_threshold,
        },
    )


OfflineEvaluator = Callable[
    [Sequence[object]],
    dict[str, object],
]


OFFLINE_INDICATOR_EVALUATORS = MappingProxyType(
    {
        BOLLINGER_BREAKOUT.strategy_name:
            evaluate_bollinger_band_breakout,

        BOLLINGER_MEAN_REVERSION.strategy_name:
            evaluate_bollinger_band_mean_reversion,

        RSI_OVERBOUGHT_MEAN_REVERSION.strategy_name:
            evaluate_rsi_overbought_mean_reversion,

        RSI_OVERSOLD_MEAN_REVERSION.strategy_name:
            evaluate_rsi_oversold_mean_reversion,
    }
)


def evaluate_offline_indicator_strategy(
    strategy_name: str,
    bars: Sequence[object],
) -> dict[str, object]:
    normalized_name = str(
        strategy_name
    ).strip()

    evaluator = OFFLINE_INDICATOR_EVALUATORS.get(
        normalized_name
    )

    if evaluator is None:
        raise KeyError(
            "No offline-qualified indicator evaluator: "
            f"{normalized_name or '<empty>'}"
        )

    return evaluator(
        bars
    )


def healthcheck() -> dict[str, object]:
    return {
        "component": "first_indicator_family_evaluators_v1",
        "healthy": True,
        "offline_evaluator_count": len(
            OFFLINE_INDICATOR_EVALUATORS
        ),
        "strategy_names": tuple(
            OFFLINE_INDICATOR_EVALUATORS
        ),
        "active_registry_modified": False,
        "owner_decision_integrated": False,
        "provider_called": False,
        "database_accessed": False,
        "execution_enabled": False,
    }
