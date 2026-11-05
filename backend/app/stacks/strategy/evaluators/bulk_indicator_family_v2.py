"""Pure offline evaluators for the second fifteen-strategy batch."""

from __future__ import annotations

from math import isfinite, sqrt
from types import MappingProxyType
from typing import Callable, Sequence

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v2 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V2,
    BulkIndicatorStrategyContractV2,
)


Bar = dict[str, object]
DecisionResult = dict[str, object]
MaybeFloat = float | None


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if isfinite(number) else None


def _extract(
    bars: Sequence[Bar],
) -> tuple[
    list[float],
    list[float],
    list[float],
    list[float],
] | None:
    closes: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    volumes: list[float] = []

    for bar in bars:
        close = _finite(bar.get("close"))
        high = _finite(bar.get("high"))
        low = _finite(bar.get("low"))
        volume = _finite(bar.get("volume"))

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
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(values)

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


def _wma(
    values: Sequence[float],
    window: int,
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(values)

    if window <= 0:
        return output

    denominator = window * (window + 1) / 2.0

    for index in range(window - 1, len(values)):
        start = index - window + 1

        output[index] = (
            sum(
                value * weight
                for weight, value in enumerate(
                    values[start:index + 1],
                    start=1,
                )
            )
            / denominator
        )

    return output


def _dense_wma(
    values: Sequence[MaybeFloat],
    window: int,
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(values)

    indexes = [
        index
        for index, value in enumerate(values)
        if value is not None
    ]

    dense = [
        float(values[index])
        for index in indexes
    ]

    calculated = _wma(
        dense,
        window,
    )

    for dense_index, original_index in enumerate(
        indexes
    ):
        output[original_index] = calculated[dense_index]

    return output


def _hma(
    values: Sequence[float],
    window: int,
) -> list[MaybeFloat]:
    half = max(
        1,
        window // 2,
    )

    root = max(
        1,
        int(
            sqrt(window)
        ),
    )

    half_values = _wma(
        values,
        half,
    )

    full_values = _wma(
        values,
        window,
    )

    raw: list[MaybeFloat] = [None] * len(values)

    for index in range(len(values)):
        if (
            half_values[index] is not None
            and full_values[index] is not None
        ):
            raw[index] = (
                2.0 * float(half_values[index])
                - float(full_values[index])
            )

    return _dense_wma(
        raw,
        root,
    )


def _true_range(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(closes)

    for index in range(1, len(closes)):
        output[index] = max(
            highs[index] - lows[index],
            abs(
                highs[index]
                - closes[index - 1]
            ),
            abs(
                lows[index]
                - closes[index - 1]
            ),
        )

    return output


def _wilder(
    values: Sequence[MaybeFloat],
    window: int,
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(values)

    dense_indexes = [
        index
        for index, value in enumerate(values)
        if value is not None
    ]

    if len(dense_indexes) < window:
        return output

    first_indexes = dense_indexes[:window]

    current = (
        sum(
            float(values[index])
            for index in first_indexes
        )
        / window
    )

    first_output_index = first_indexes[-1]
    output[first_output_index] = current

    for index in dense_indexes[window:]:
        current = (
            current * (window - 1)
            + float(values[index])
        ) / window

        output[index] = current

    return output


def _atr(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
) -> list[MaybeFloat]:
    return _wilder(
        _true_range(
            closes,
            highs,
            lows,
        ),
        window,
    )


def _dmi_adx(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
) -> tuple[
    list[MaybeFloat],
    list[MaybeFloat],
    list[MaybeFloat],
]:
    count = len(closes)

    plus_dm: list[MaybeFloat] = [None] * count
    minus_dm: list[MaybeFloat] = [None] * count

    for index in range(1, count):
        up_move = (
            highs[index]
            - highs[index - 1]
        )

        down_move = (
            lows[index - 1]
            - lows[index]
        )

        plus_dm[index] = (
            up_move
            if (
                up_move > down_move
                and up_move > 0.0
            )
            else 0.0
        )

        minus_dm[index] = (
            down_move
            if (
                down_move > up_move
                and down_move > 0.0
            )
            else 0.0
        )

    atr_values = _atr(
        closes,
        highs,
        lows,
        window,
    )

    smoothed_plus = _wilder(
        plus_dm,
        window,
    )

    smoothed_minus = _wilder(
        minus_dm,
        window,
    )

    plus_di: list[MaybeFloat] = [None] * count
    minus_di: list[MaybeFloat] = [None] * count
    dx: list[MaybeFloat] = [None] * count

    for index in range(count):
        atr_value = atr_values[index]
        plus_value = smoothed_plus[index]
        minus_value = smoothed_minus[index]

        if (
            atr_value is None
            or plus_value is None
            or minus_value is None
            or atr_value <= 0.0
        ):
            continue

        plus_di[index] = (
            100.0
            * float(plus_value)
            / float(atr_value)
        )

        minus_di[index] = (
            100.0
            * float(minus_value)
            / float(atr_value)
        )

        total = (
            float(plus_di[index])
            + float(minus_di[index])
        )

        dx[index] = (
            0.0
            if total == 0.0
            else (
                100.0
                * abs(
                    float(plus_di[index])
                    - float(minus_di[index])
                )
                / total
            )
        )

    adx = _wilder(
        dx,
        window,
    )

    return plus_di, minus_di, adx


def _stochastic(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    k_window: int,
    d_window: int,
) -> tuple[
    list[MaybeFloat],
    list[MaybeFloat],
]:
    k_values: list[MaybeFloat] = [None] * len(closes)

    for index in range(
        k_window - 1,
        len(closes),
    ):
        start = (
            index
            - k_window
            + 1
        )

        highest = max(
            highs[start:index + 1]
        )

        lowest = min(
            lows[start:index + 1]
        )

        width = highest - lowest

        if width > 0.0:
            k_values[index] = (
                100.0
                * (
                    closes[index]
                    - lowest
                )
                / width
            )

    d_values: list[MaybeFloat] = [None] * len(closes)

    dense_indexes = [
        index
        for index, value in enumerate(k_values)
        if value is not None
    ]

    dense_values = [
        float(k_values[index])
        for index in dense_indexes
    ]

    dense_sma = _sma(
        dense_values,
        d_window,
    )

    for dense_index, original_index in enumerate(
        dense_indexes
    ):
        d_values[original_index] = dense_sma[dense_index]

    return k_values, d_values


def _percentile_rank(
    values: Sequence[MaybeFloat],
    window: int,
) -> list[MaybeFloat]:
    output: list[MaybeFloat] = [None] * len(values)

    for index in range(
        window - 1,
        len(values),
    ):
        sample = values[
            index - window + 1:
            index + 1
        ]

        if any(
            value is None
            for value in sample
        ):
            continue

        current = float(sample[-1])

        less_or_equal = sum(
            1
            for value in sample
            if float(value) <= current
        )

        output[index] = (
            100.0
            * less_or_equal
            / window
        )

    return output


def _mfi(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    volumes: Sequence[float],
    window: int,
) -> list[MaybeFloat]:
    typical = [
        (
            high
            + low
            + close
        ) / 3.0
        for high, low, close in zip(
            highs,
            lows,
            closes,
            strict=True,
        )
    ]

    positive = [0.0] * len(closes)
    negative = [0.0] * len(closes)

    for index in range(1, len(closes)):
        flow = (
            typical[index]
            * volumes[index]
        )

        if typical[index] > typical[index - 1]:
            positive[index] = flow
        elif typical[index] < typical[index - 1]:
            negative[index] = flow

    output: list[MaybeFloat] = [None] * len(closes)

    for index in range(window, len(closes)):
        start = index - window + 1

        positive_sum = sum(
            positive[start:index + 1]
        )

        negative_sum = sum(
            negative[start:index + 1]
        )

        if negative_sum == 0.0:
            output[index] = (
                100.0
                if positive_sum > 0.0
                else 50.0
            )
        else:
            ratio = (
                positive_sum
                / negative_sum
            )

            output[index] = (
                100.0
                - 100.0
                / (
                    1.0
                    + ratio
                )
            )

    return output


def _pair(
    values: Sequence[MaybeFloat],
) -> tuple[float, float] | None:
    if len(values) < 2:
        return None

    previous = values[-2]
    current = values[-1]

    if (
        previous is None
        or current is None
    ):
        return None

    return (
        float(previous),
        float(current),
    )


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
    contract: BulkIndicatorStrategyContractV2,
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
        "strategy_name":
            contract.strategy_name,
        "evaluator_id":
            contract.evaluator_id,
        "decision":
            decision,
        "signal":
            decision,
        "confidence":
            0.0
            if decision in (
                "HOLD",
                "ABSTAIN",
            )
            else bounded,
        "reason":
            reason,
        **evidence,
    }


def _abstain(
    contract: BulkIndicatorStrategyContractV2,
    reason: str,
) -> DecisionResult:
    return _result(
        contract,
        "ABSTAIN",
        reason,
    )


def _final(
    contract: BulkIndicatorStrategyContractV2,
    buy: bool,
    sell: bool,
    strength: float,
    evidence: dict[str, object],
) -> DecisionResult:
    if buy and sell:
        return _abstain(
            contract,
            "ambiguous_directional_conditions",
        )

    if buy:
        return _result(
            contract,
            "BUY",
            "bullish_contract_condition",
            strength,
            **evidence,
        )

    if sell:
        return _result(
            contract,
            "SELL",
            "bearish_contract_condition",
            strength,
            **evidence,
        )

    return _result(
        contract,
        "HOLD",
        "no_contract_condition",
        0.0,
        **evidence,
    )


def _evaluate(
    contract: BulkIndicatorStrategyContractV2,
    bars: Sequence[Bar],
) -> DecisionResult:
    if len(bars) < contract.minimum_bars:
        return _abstain(
            contract,
            "insufficient_truthful_bars",
        )

    extracted = _extract(
        bars
    )

    if extracted is None:
        return _abstain(
            contract,
            "invalid_truthful_bars",
        )

    closes, highs, lows, volumes = extracted
    parameters = contract.parameters
    name = contract.strategy_name

    buy = False
    sell = False
    strength = 0.0
    evidence: dict[str, object] = {}

    if name == "Stochastic Pullback in Trend":
        k_values, d_values = _stochastic(
            closes,
            highs,
            lows,
            int(parameters["k_window"]),
            int(parameters["d_window"]),
        )

        k_pair = _pair(k_values)
        d_pair = _pair(d_values)
        trend = _sma(
            closes,
            int(parameters["trend_sma"]),
        )

        if (
            k_pair is None
            or d_pair is None
            or trend[-1] is None
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        oversold = float(
            parameters["oversold_threshold"]
        )

        overbought = float(
            parameters["overbought_threshold"]
        )

        buy = (
            closes[-1] > float(trend[-1])
            and k_pair[0] <= oversold
            and _cross_up(
                k_pair[0],
                k_pair[1],
                d_pair[0],
                d_pair[1],
            )
        )

        sell = (
            closes[-1] < float(trend[-1])
            and k_pair[0] >= overbought
            and _cross_down(
                k_pair[0],
                k_pair[1],
                d_pair[0],
                d_pair[1],
            )
        )

        strength = (
            abs(
                k_pair[1]
                - d_pair[1]
            )
            / 100.0
        )

        evidence.update(
            {
                "current_percent_k": k_pair[1],
                "current_percent_d": d_pair[1],
                "current_trend_sma": float(trend[-1]),
            }
        )

    elif name == "High-Low Momentum":
        window = int(
            parameters["window"]
        )

        scores: list[MaybeFloat] = [None] * len(closes)

        for index in range(
            window - 1,
            len(closes),
        ):
            start = index - window + 1
            highest = max(
                highs[start:index + 1]
            )
            lowest = min(
                lows[start:index + 1]
            )
            width = highest - lowest

            if width > 0.0:
                scores[index] = (
                    closes[index]
                    - lowest
                ) / width

        pair = _pair(scores)

        if pair is None:
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        bullish = float(
            parameters["bullish_threshold"]
        )

        bearish = float(
            parameters["bearish_threshold"]
        )

        buy = _cross_up(
            pair[0],
            pair[1],
            bullish,
            bullish,
        )

        sell = _cross_down(
            pair[0],
            pair[1],
            bearish,
            bearish,
        )

        strength = abs(
            pair[1] - 0.5
        ) * 2.0

        evidence[
            "current_range_position"
        ] = pair[1]

    elif name == "Price Acceleration":
        velocity_window = int(
            parameters["velocity_window"]
        )

        lag = int(
            parameters["acceleration_lag"]
        )

        current_velocity = (
            closes[-1]
            - closes[-1 - velocity_window]
        )

        prior_velocity = (
            closes[-1 - lag]
            - closes[-1 - lag - velocity_window]
        )

        acceleration = (
            current_velocity
            - prior_velocity
        )

        buy = (
            current_velocity > 0.0
            and acceleration > 0.0
        )

        sell = (
            current_velocity < 0.0
            and acceleration < 0.0
        )

        strength = (
            abs(acceleration)
            / max(
                abs(closes[-1]),
                1.0,
            )
        )

        evidence.update(
            {
                "current_velocity": current_velocity,
                "current_acceleration": acceleration,
            }
        )

    elif name in (
        "ADX Breakout",
        "ADX Trend Following",
        "DMI Crossover",
    ):
        window = int(
            parameters.get(
                "adx_window",
                parameters.get(
                    "window",
                    14,
                ),
            )
        )

        plus_di, minus_di, adx = _dmi_adx(
            closes,
            highs,
            lows,
            window,
        )

        plus_pair = _pair(plus_di)
        minus_pair = _pair(minus_di)

        if (
            plus_pair is None
            or minus_pair is None
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        current_adx = (
            None
            if adx[-1] is None
            else float(adx[-1])
        )

        if name == "ADX Breakout":
            if current_adx is None:
                return _abstain(
                    contract,
                    "indicator_unavailable",
                )

            breakout_window = int(
                parameters["breakout_window"]
            )

            prior_high = max(
                highs[
                    -breakout_window - 1:
                    -1
                ]
            )

            prior_low = min(
                lows[
                    -breakout_window - 1:
                    -1
                ]
            )

            threshold = float(
                parameters["adx_threshold"]
            )

            buy = (
                closes[-1] > prior_high
                and current_adx >= threshold
                and plus_pair[1] > minus_pair[1]
            )

            sell = (
                closes[-1] < prior_low
                and current_adx >= threshold
                and minus_pair[1] > plus_pair[1]
            )

        elif name == "ADX Trend Following":
            if current_adx is None:
                return _abstain(
                    contract,
                    "indicator_unavailable",
                )

            threshold = float(
                parameters["adx_threshold"]
            )

            buy = (
                current_adx >= threshold
                and plus_pair[1] > minus_pair[1]
            )

            sell = (
                current_adx >= threshold
                and minus_pair[1] > plus_pair[1]
            )

        else:
            buy = _cross_up(
                plus_pair[0],
                plus_pair[1],
                minus_pair[0],
                minus_pair[1],
            )

            sell = _cross_down(
                plus_pair[0],
                plus_pair[1],
                minus_pair[0],
                minus_pair[1],
            )

        strength = (
            abs(
                plus_pair[1]
                - minus_pair[1]
            )
            / 100.0
        )

        evidence.update(
            {
                "current_plus_di": plus_pair[1],
                "current_minus_di": minus_pair[1],
                "current_adx": current_adx,
            }
        )

    elif name == "Hull Moving Average Trend":
        values = _hma(
            closes,
            int(parameters["window"]),
        )

        pair = _pair(values)

        if pair is None:
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        slope = (
            pair[1]
            - pair[0]
        )

        buy = slope > 0.0
        sell = slope < 0.0

        strength = (
            abs(slope)
            / max(
                abs(pair[1]),
                1.0,
            )
        )

        evidence.update(
            {
                "current_hma": pair[1],
                "current_hma_slope": slope,
            }
        )

    elif name == "Moving Average Ribbon":
        periods = (
            int(parameters["ma_1"]),
            int(parameters["ma_2"]),
            int(parameters["ma_3"]),
            int(parameters["ma_4"]),
            int(parameters["ma_5"]),
        )

        values = [
            _sma(
                closes,
                period,
            )[-1]
            for period in periods
        ]

        if any(
            value is None
            for value in values
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        numbers = [
            float(value)
            for value in values
        ]

        buy = all(
            left > right
            for left, right in zip(
                numbers,
                numbers[1:],
            )
        )

        sell = all(
            left < right
            for left, right in zip(
                numbers,
                numbers[1:],
            )
        )

        strength = (
            abs(
                numbers[0]
                - numbers[-1]
            )
            / max(
                abs(numbers[-1]),
                1.0,
            )
        )

        evidence[
            "current_ribbon"
        ] = tuple(numbers)

    elif name in (
        "Envelope Mean Reversion",
        "Moving Average Deviation Reversion",
    ):
        window = int(
            parameters["sma_window"]
        )

        sma_values = _sma(
            closes,
            window,
        )

        sma_pair = _pair(sma_values)

        if sma_pair is None:
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        if name == "Envelope Mean Reversion":
            fraction = float(
                parameters["envelope_fraction"]
            )

            prior_lower = (
                sma_pair[0]
                * (1.0 - fraction)
            )

            current_lower = (
                sma_pair[1]
                * (1.0 - fraction)
            )

            prior_upper = (
                sma_pair[0]
                * (1.0 + fraction)
            )

            current_upper = (
                sma_pair[1]
                * (1.0 + fraction)
            )

            buy = _cross_down(
                closes[-2],
                closes[-1],
                prior_lower,
                current_lower,
            )

            sell = _cross_up(
                closes[-2],
                closes[-1],
                prior_upper,
                current_upper,
            )

            evidence.update(
                {
                    "current_lower_envelope": current_lower,
                    "current_upper_envelope": current_upper,
                }
            )

        else:
            prior_deviation = (
                closes[-2]
                / sma_pair[0]
                - 1.0
            )

            current_deviation = (
                closes[-1]
                / sma_pair[1]
                - 1.0
            )

            oversold = float(
                parameters["oversold_deviation"]
            )

            overbought = float(
                parameters["overbought_deviation"]
            )

            buy = _cross_down(
                prior_deviation,
                current_deviation,
                oversold,
                oversold,
            )

            sell = _cross_up(
                prior_deviation,
                current_deviation,
                overbought,
                overbought,
            )

            evidence[
                "current_deviation"
            ] = current_deviation

        strength = (
            abs(
                closes[-1]
                - sma_pair[1]
            )
            / max(
                abs(sma_pair[1]),
                1.0,
            )
        )

    elif name == "Moving Average Crossover with ATR Filter":
        fast = _sma(
            closes,
            int(parameters["fast_sma"]),
        )

        slow = _sma(
            closes,
            int(parameters["slow_sma"]),
        )

        atr_values = _atr(
            closes,
            highs,
            lows,
            int(parameters["atr_window"]),
        )

        fast_pair = _pair(fast)
        slow_pair = _pair(slow)

        current_atr = atr_values[-1]

        if (
            fast_pair is None
            or slow_pair is None
            or current_atr is None
            or current_atr <= 0.0
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        separation = abs(
            fast_pair[1]
            - slow_pair[1]
        )

        required = (
            float(
                parameters[
                    "separation_atr_ratio"
                ]
            )
            * float(current_atr)
        )

        buy = (
            separation > required
            and _cross_up(
                fast_pair[0],
                fast_pair[1],
                slow_pair[0],
                slow_pair[1],
            )
        )

        sell = (
            separation > required
            and _cross_down(
                fast_pair[0],
                fast_pair[1],
                slow_pair[0],
                slow_pair[1],
            )
        )

        strength = (
            separation
            / max(
                float(current_atr),
                1.0,
            )
        )

        evidence.update(
            {
                "current_fast_sma": fast_pair[1],
                "current_slow_sma": slow_pair[1],
                "current_atr": float(current_atr),
            }
        )

    elif name == "Moving Average Slope":
        values = _sma(
            closes,
            int(parameters["sma_window"]),
        )

        lag = int(
            parameters["slope_lag"]
        )

        current = values[-1]
        previous = values[-1 - lag]

        if (
            current is None
            or previous is None
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        slope = (
            float(current)
            - float(previous)
        ) / lag

        buy = slope > 0.0
        sell = slope < 0.0

        strength = (
            abs(slope)
            / max(
                abs(float(current)),
                1.0,
            )
        )

        evidence[
            "current_sma_slope"
        ] = slope

    elif name == "Triple Moving Average Trend":
        short = _sma(
            closes,
            int(parameters["short_sma"]),
        )[-1]

        medium = _sma(
            closes,
            int(parameters["medium_sma"]),
        )[-1]

        long_value = _sma(
            closes,
            int(parameters["long_sma"]),
        )[-1]

        if (
            short is None
            or medium is None
            or long_value is None
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        buy = (
            float(short)
            > float(medium)
            > float(long_value)
        )

        sell = (
            float(short)
            < float(medium)
            < float(long_value)
        )

        strength = (
            abs(
                float(short)
                - float(long_value)
            )
            / max(
                abs(float(long_value)),
                1.0,
            )
        )

        evidence.update(
            {
                "current_short_sma": float(short),
                "current_medium_sma": float(medium),
                "current_long_sma": float(long_value),
            }
        )

    elif name == "ATR Compression Expansion":
        atr_values = _atr(
            closes,
            highs,
            lows,
            int(parameters["atr_window"]),
        )

        percentiles = _percentile_rank(
            atr_values,
            int(parameters["percentile_window"]),
        )

        atr_pair = _pair(atr_values)
        percentile_pair = _pair(percentiles)

        if (
            atr_pair is None
            or percentile_pair is None
        ):
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        breakout_window = int(
            parameters["breakout_window"]
        )

        prior_high = max(
            highs[
                -breakout_window - 1:
                -1
            ]
        )

        prior_low = min(
            lows[
                -breakout_window - 1:
                -1
            ]
        )

        compressed = (
            percentile_pair[0]
            <= float(
                parameters[
                    "compression_percentile"
                ]
            )
        )

        expanded = (
            atr_pair[1]
            > atr_pair[0]
        )

        buy = (
            compressed
            and expanded
            and closes[-1] > prior_high
        )

        sell = (
            compressed
            and expanded
            and closes[-1] < prior_low
        )

        strength = (
            abs(
                atr_pair[1]
                - atr_pair[0]
            )
            / max(
                abs(atr_pair[0]),
                1.0,
            )
        )

        evidence.update(
            {
                "current_atr": atr_pair[1],
                "previous_atr_percentile": percentile_pair[0],
            }
        )

    elif name == "Money Flow Index Reversion":
        values = _mfi(
            closes,
            highs,
            lows,
            volumes,
            int(parameters["window"]),
        )

        pair = _pair(values)

        if pair is None:
            return _abstain(
                contract,
                "indicator_unavailable",
            )

        oversold = float(
            parameters["oversold_threshold"]
        )

        overbought = float(
            parameters["overbought_threshold"]
        )

        buy = _cross_up(
            pair[0],
            pair[1],
            oversold,
            oversold,
        )

        sell = _cross_down(
            pair[0],
            pair[1],
            overbought,
            overbought,
        )

        strength = (
            abs(
                pair[1]
                - 50.0
            )
            / 50.0
        )

        evidence[
            "current_mfi"
        ] = pair[1]

    else:
        return _abstain(
            contract,
            "unsupported_contract",
        )

    return _final(
        contract,
        buy,
        sell,
        strength,
        evidence,
    )


def _make_evaluator(
    strategy_name: str,
) -> Callable[
    [Sequence[Bar]],
    DecisionResult,
]:
    contract = BULK_INDICATOR_STRATEGY_CONTRACTS_V2[
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
        + contract.evaluator_id.removesuffix(
            "_v1"
        )
    )

    evaluator.__qualname__ = evaluator.__name__

    return evaluator


BULK_OFFLINE_EVALUATORS_V2 = MappingProxyType(
    {
        name: _make_evaluator(
            name
        )
        for name in BULK_INDICATOR_STRATEGY_CONTRACTS_V2
    }
)


def evaluate_bulk_indicator_strategy_v2(
    strategy_name: str,
    bars: Sequence[Bar],
) -> DecisionResult:
    evaluator = BULK_OFFLINE_EVALUATORS_V2.get(
        str(
            strategy_name
        ).strip()
    )

    if evaluator is None:
        raise KeyError(
            "No second-batch offline evaluator: "
            f"{strategy_name!r}"
        )

    return evaluator(
        bars
    )


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_offline_evaluators_v2",
        "healthy": True,
        "evaluator_count": len(
            BULK_OFFLINE_EVALUATORS_V2
        ),
        "strategy_names": tuple(
            BULK_OFFLINE_EVALUATORS_V2
        ),
        "pure_functions": True,
        "provider_called": False,
        "database_accessed": False,
        "position_sizing_enabled": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }
