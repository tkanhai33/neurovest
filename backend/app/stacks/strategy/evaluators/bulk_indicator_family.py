"""Pure offline evaluators for the first fifteen-strategy bulk batch."""

from __future__ import annotations

from math import isfinite
from types import MappingProxyType
from typing import Callable, Sequence

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts import (
    BULK_INDICATOR_STRATEGY_CONTRACTS,
    BulkIndicatorStrategyContract,
)


DecisionResult = dict[str, object]
Bar = dict[str, object]


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _extract(
    bars: Sequence[Bar],
) -> tuple[list[float], list[float], list[float], list[float]] | None:
    closes: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    volumes: list[float] = []

    for bar in bars:
        close = _finite(bar.get("close"))
        high = _finite(bar.get("high"))
        low = _finite(bar.get("low"))
        volume = _finite(bar.get("volume", 0.0))

        if (
            close is None
            or high is None
            or low is None
            or volume is None
            or close <= 0.0
            or high < low
            or high < close
            or low > close
            or volume < 0.0
        ):
            return None

        closes.append(close)
        highs.append(high)
        lows.append(low)
        volumes.append(volume)

    return closes, highs, lows, volumes


def _sma(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(values)

    if window <= 0:
        return output

    running = 0.0

    for index, value in enumerate(values):
        running += value

        if index >= window:
            running -= values[index - window]

        if index >= window - 1:
            output[index] = running / window

    return output


def _ema(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(values)

    if window <= 0 or len(values) < window:
        return output

    seed = sum(values[:window]) / window
    output[window - 1] = seed
    alpha = 2.0 / (window + 1.0)
    current = seed

    for index in range(window, len(values)):
        current = (
            alpha * values[index]
            + (1.0 - alpha) * current
        )
        output[index] = current

    return output


def _dense_ema(
    values: Sequence[float | None],
    window: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    dense_indexes = [
        index
        for index, value in enumerate(values)
        if value is not None
    ]

    if len(dense_indexes) < window:
        return output

    dense_values = [
        float(values[index])
        for index in dense_indexes
    ]

    dense_result = _ema(
        dense_values,
        window,
    )

    for dense_index, original_index in enumerate(
        dense_indexes
    ):
        output[original_index] = dense_result[dense_index]

    return output


def _macd(
    closes: Sequence[float],
    fast: int,
    slow: int,
    signal: int,
) -> tuple[
    list[float | None],
    list[float | None],
    list[float | None],
]:
    fast_values = _ema(closes, fast)
    slow_values = _ema(closes, slow)
    macd: list[float | None] = [None] * len(closes)

    for index in range(len(closes)):
        if (
            fast_values[index] is not None
            and slow_values[index] is not None
        ):
            macd[index] = (
                float(fast_values[index])
                - float(slow_values[index])
            )

    signal_values = _dense_ema(macd, signal)
    histogram: list[float | None] = [None] * len(closes)

    for index in range(len(closes)):
        if (
            macd[index] is not None
            and signal_values[index] is not None
        ):
            histogram[index] = (
                float(macd[index])
                - float(signal_values[index])
            )

    return macd, signal_values, histogram


def _stochastic(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    k_window: int,
    d_window: int,
) -> tuple[list[float | None], list[float | None]]:
    k_values: list[float | None] = [None] * len(closes)

    for index in range(k_window - 1, len(closes)):
        start = index - k_window + 1
        highest = max(highs[start:index + 1])
        lowest = min(lows[start:index + 1])
        width = highest - lowest

        if width > 0.0:
            k_values[index] = (
                100.0
                * (closes[index] - lowest)
                / width
            )

    d_values = _dense_ema(k_values, d_window)
    return k_values, d_values


def _cci(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
    scaling: float,
) -> list[float | None]:
    typical = [
        (high + low + close) / 3.0
        for high, low, close in zip(
            highs,
            lows,
            closes,
            strict=True,
        )
    ]

    means = _sma(typical, window)
    output: list[float | None] = [None] * len(closes)

    for index in range(window - 1, len(closes)):
        mean = means[index]

        if mean is None:
            continue

        start = index - window + 1
        deviation = (
            sum(
                abs(value - mean)
                for value in typical[start:index + 1]
            )
            / window
        )

        if deviation > 0.0:
            output[index] = (
                (typical[index] - mean)
                / (scaling * deviation)
            )
        else:
            output[index] = 0.0

    return output


def _roc(
    closes: Sequence[float],
    window: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(closes)

    for index in range(window, len(closes)):
        reference = closes[index - window]

        if reference > 0.0:
            output[index] = (
                100.0
                * (
                    closes[index]
                    / reference
                    - 1.0
                )
            )

    return output


def _rsi(
    closes: Sequence[float],
    window: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(closes)

    if len(closes) <= window:
        return output

    gains = []
    losses = []

    for index in range(1, window + 1):
        change = closes[index] - closes[index - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    average_gain = sum(gains) / window
    average_loss = sum(losses) / window

    def score() -> float:
        if average_loss == 0.0:
            return 100.0 if average_gain > 0.0 else 50.0
        ratio = average_gain / average_loss
        return 100.0 - 100.0 / (1.0 + ratio)

    output[window] = score()

    for index in range(window + 1, len(closes)):
        change = closes[index] - closes[index - 1]
        gain = max(change, 0.0)
        loss = max(-change, 0.0)

        average_gain = (
            (average_gain * (window - 1) + gain)
            / window
        )
        average_loss = (
            (average_loss * (window - 1) + loss)
            / window
        )

        output[index] = score()

    return output


def _trix(
    closes: Sequence[float],
    window: int,
) -> list[float | None]:
    first = _ema(closes, window)
    second = _dense_ema(first, window)
    third = _dense_ema(second, window)
    output: list[float | None] = [None] * len(closes)

    for index in range(1, len(closes)):
        previous = third[index - 1]
        current = third[index]

        if (
            previous is not None
            and current is not None
            and float(previous) != 0.0
        ):
            output[index] = (
                100.0
                * (
                    float(current)
                    / float(previous)
                    - 1.0
                )
            )

    return output


def _cross_up(
    previous: float,
    current: float,
    previous_level: float,
    current_level: float,
) -> bool:
    return (
        previous <= previous_level
        and current > current_level
    )


def _cross_down(
    previous: float,
    current: float,
    previous_level: float,
    current_level: float,
) -> bool:
    return (
        previous >= previous_level
        and current < current_level
    )


def _result(
    contract: BulkIndicatorStrategyContract,
    decision: str,
    reason: str,
    confidence: float = 0.0,
    **evidence: object,
) -> DecisionResult:
    bounded = max(
        0.0,
        min(
            1.0,
            float(confidence),
        ),
    )

    return {
        "status":
            "abstain"
            if decision == "ABSTAIN"
            else "ok",
        "strategy_name": contract.strategy_name,
        "evaluator_id": contract.evaluator_id,
        "decision": decision,
        "signal": decision,
        "confidence":
            0.0
            if decision in ("HOLD", "ABSTAIN")
            else bounded,
        "reason": reason,
        **evidence,
    }


def _abstain(
    contract: BulkIndicatorStrategyContract,
    reason: str,
) -> DecisionResult:
    return _result(
        contract,
        "ABSTAIN",
        reason,
    )


def _pair(
    values: Sequence[float | None],
) -> tuple[float, float] | None:
    if len(values) < 2:
        return None

    previous = values[-2]
    current = values[-1]

    if previous is None or current is None:
        return None

    return float(previous), float(current)


def _evaluate(
    contract: BulkIndicatorStrategyContract,
    bars: Sequence[Bar],
) -> DecisionResult:
    if len(bars) < contract.minimum_bars:
        return _abstain(
            contract,
            "insufficient_truthful_bars",
        )

    extracted = _extract(bars)

    if extracted is None:
        return _abstain(
            contract,
            "invalid_truthful_bars",
        )

    closes, highs, lows, _ = extracted
    parameters = contract.parameters
    name = contract.strategy_name

    buy = False
    sell = False
    evidence: dict[str, object] = {}
    strength = 0.0

    if name in (
        "MACD Crossover",
        "MACD Zero-Line",
        "MACD Histogram Momentum",
    ):
        fast = int(parameters["fast_ema"])
        slow = int(parameters["slow_ema"])
        signal = int(parameters.get("signal_ema", 1))
        macd, signal_values, histogram = _macd(
            closes,
            fast,
            slow,
            signal,
        )

        if name == "MACD Crossover":
            macd_pair = _pair(macd)
            signal_pair = _pair(signal_values)

            if macd_pair is None or signal_pair is None:
                return _abstain(contract, "indicator_unavailable")

            buy = _cross_up(
                macd_pair[0],
                macd_pair[1],
                signal_pair[0],
                signal_pair[1],
            )
            sell = _cross_down(
                macd_pair[0],
                macd_pair[1],
                signal_pair[0],
                signal_pair[1],
            )
            strength = abs(macd_pair[1] - signal_pair[1])
            evidence["current_macd"] = macd_pair[1]
            evidence["current_signal"] = signal_pair[1]

        elif name == "MACD Zero-Line":
            pair = _pair(macd)

            if pair is None:
                return _abstain(contract, "indicator_unavailable")

            buy = _cross_up(pair[0], pair[1], 0.0, 0.0)
            sell = _cross_down(pair[0], pair[1], 0.0, 0.0)
            strength = abs(pair[1])
            evidence["current_macd"] = pair[1]

        else:
            pair = _pair(histogram)

            if pair is None:
                return _abstain(contract, "indicator_unavailable")

            buy = _cross_up(pair[0], pair[1], 0.0, 0.0)
            sell = _cross_down(pair[0], pair[1], 0.0, 0.0)
            strength = abs(pair[1])
            evidence["current_histogram"] = pair[1]

    elif name in (
        "Stochastic Momentum",
        "Stochastic Oversold Reversion",
    ):
        k_values, d_values = _stochastic(
            closes,
            highs,
            lows,
            int(parameters["k_window"]),
            int(parameters["d_window"]),
        )
        k_pair = _pair(k_values)
        d_pair = _pair(d_values)

        if k_pair is None or d_pair is None:
            return _abstain(contract, "indicator_unavailable")

        bullish_cross = _cross_up(
            k_pair[0],
            k_pair[1],
            d_pair[0],
            d_pair[1],
        )
        bearish_cross = _cross_down(
            k_pair[0],
            k_pair[1],
            d_pair[0],
            d_pair[1],
        )

        if name == "Stochastic Momentum":
            center = float(parameters["center_threshold"])
            buy = bullish_cross and k_pair[1] > center
            sell = bearish_cross and k_pair[1] < center
        else:
            oversold = float(parameters["oversold_threshold"])
            buy = bullish_cross and k_pair[0] <= oversold
            sell = False

        strength = abs(k_pair[1] - d_pair[1]) / 100.0
        evidence["current_percent_k"] = k_pair[1]
        evidence["current_percent_d"] = d_pair[1]

    elif name in (
        "Commodity Channel Index Momentum",
        "CCI Mean Reversion",
    ):
        values = _cci(
            closes,
            highs,
            lows,
            int(parameters["window"]),
            float(parameters["scaling_constant"]),
        )
        pair = _pair(values)

        if pair is None:
            return _abstain(contract, "indicator_unavailable")

        if name == "Commodity Channel Index Momentum":
            positive = float(parameters["positive_threshold"])
            negative = float(parameters["negative_threshold"])
            buy = _cross_up(pair[0], pair[1], positive, positive)
            sell = _cross_down(pair[0], pair[1], negative, negative)
        else:
            oversold = float(parameters["oversold_threshold"])
            overbought = float(parameters["overbought_threshold"])
            buy = pair[0] <= oversold and pair[1] > oversold
            sell = pair[0] >= overbought and pair[1] < overbought

        strength = abs(pair[1]) / 200.0
        evidence["current_cci"] = pair[1]

    elif name in (
        "Rate of Change Momentum",
        "ROC Zero Cross",
        "Time-Series Momentum",
    ):
        window = int(
            parameters.get(
                "window",
                parameters.get("lookback", 1),
            )
        )
        values = _roc(closes, window)
        pair = _pair(values)

        if pair is None:
            return _abstain(contract, "indicator_unavailable")

        if name == "Rate of Change Momentum":
            positive = float(parameters["positive_threshold"])
            negative = float(parameters["negative_threshold"])
            buy = _cross_up(pair[0], pair[1], positive, positive)
            sell = _cross_down(pair[0], pair[1], negative, negative)
        elif name == "ROC Zero Cross":
            buy = _cross_up(pair[0], pair[1], 0.0, 0.0)
            sell = _cross_down(pair[0], pair[1], 0.0, 0.0)
        else:
            buy = pair[1] > 0.0
            sell = pair[1] < 0.0

        strength = abs(pair[1]) / 100.0
        evidence["current_roc"] = pair[1]

    elif name == "RSI Momentum":
        values = _rsi(
            closes,
            int(parameters["window"]),
        )
        pair = _pair(values)

        if pair is None:
            return _abstain(contract, "indicator_unavailable")

        threshold = float(parameters["momentum_threshold"])
        buy = _cross_up(pair[0], pair[1], threshold, threshold)
        sell = _cross_down(pair[0], pair[1], threshold, threshold)
        strength = abs(pair[1] - threshold) / 50.0
        evidence["current_rsi"] = pair[1]

    elif name == "TRIX Trend":
        values = _trix(
            closes,
            int(parameters["ema_window"]),
        )
        pair = _pair(values)

        if pair is None:
            return _abstain(contract, "indicator_unavailable")

        buy = _cross_up(pair[0], pair[1], 0.0, 0.0)
        sell = _cross_down(pair[0], pair[1], 0.0, 0.0)
        strength = abs(pair[1]) / 10.0
        evidence["current_trix"] = pair[1]

    elif name in (
        "Golden Cross",
        "Exponential Moving Average Crossover",
        "Price Above Moving Average",
    ):
        if name == "Golden Cross":
            fast_values = _sma(
                closes,
                int(parameters["fast_sma"]),
            )
            slow_values = _sma(
                closes,
                int(parameters["slow_sma"]),
            )
        elif name == "Exponential Moving Average Crossover":
            fast_values = _ema(
                closes,
                int(parameters["fast_ema"]),
            )
            slow_values = _ema(
                closes,
                int(parameters["slow_ema"]),
            )
        else:
            fast_values = [float(value) for value in closes]
            slow_values = _sma(
                closes,
                int(parameters["sma_window"]),
            )

        fast_pair = _pair(fast_values)
        slow_pair = _pair(slow_values)

        if fast_pair is None or slow_pair is None:
            return _abstain(contract, "indicator_unavailable")

        buy = _cross_up(
            fast_pair[0],
            fast_pair[1],
            slow_pair[0],
            slow_pair[1],
        )
        sell = _cross_down(
            fast_pair[0],
            fast_pair[1],
            slow_pair[0],
            slow_pair[1],
        )
        strength = abs(fast_pair[1] - slow_pair[1]) / max(
            abs(slow_pair[1]),
            1.0,
        )
        evidence["current_fast_value"] = fast_pair[1]
        evidence["current_slow_value"] = slow_pair[1]

    else:
        return _abstain(
            contract,
            "unsupported_contract",
        )

    if buy and sell:
        return _abstain(
            contract,
            "ambiguous_directional_conditions",
        )

    if buy:
        return _result(
            contract,
            "BUY",
            "bullish_contract_transition",
            strength,
            **evidence,
        )

    if sell:
        return _result(
            contract,
            "SELL",
            "bearish_contract_transition",
            strength,
            **evidence,
        )

    return _result(
        contract,
        "HOLD",
        "no_new_contract_transition",
        0.0,
        **evidence,
    )


def _make_evaluator(
    strategy_name: str,
) -> Callable[[Sequence[Bar]], DecisionResult]:
    contract = BULK_INDICATOR_STRATEGY_CONTRACTS[
        strategy_name
    ]

    def evaluator(
        bars: Sequence[Bar],
    ) -> DecisionResult:
        return _evaluate(
            contract,
            bars,
        )

    evaluator.__name__ = (
        "evaluate_"
        + contract.evaluator_id.removesuffix("_v1")
    )
    evaluator.__qualname__ = evaluator.__name__
    return evaluator


BULK_OFFLINE_EVALUATORS = MappingProxyType(
    {
        name: _make_evaluator(name)
        for name in BULK_INDICATOR_STRATEGY_CONTRACTS
    }
)


def evaluate_bulk_indicator_strategy(
    strategy_name: str,
    bars: Sequence[Bar],
) -> DecisionResult:
    evaluator = BULK_OFFLINE_EVALUATORS.get(
        str(strategy_name).strip()
    )

    if evaluator is None:
        raise KeyError(
            "No offline bulk evaluator: "
            f"{strategy_name!r}"
        )

    return evaluator(bars)


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_offline_evaluators_v1",
        "healthy": True,
        "evaluator_count": len(BULK_OFFLINE_EVALUATORS),
        "strategy_names": tuple(BULK_OFFLINE_EVALUATORS),
        "pure_functions": True,
        "provider_called": False,
        "database_accessed": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }
