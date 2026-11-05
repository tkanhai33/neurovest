"""Pure deterministic evaluators for the third daily-OHLCV batch."""

from __future__ import annotations

from math import isfinite, sqrt
from statistics import fmean
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v3 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V3,
    BulkIndicatorStrategyContractV3,
)


Bar = Mapping[str, Any]
Evaluator = Callable[[Sequence[Bar]], dict[str, object]]


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None

    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if not isfinite(converted):
        return None

    return converted


def _extract(
    bars: Sequence[Bar] | None,
) -> tuple[
    list[float],
    list[float],
    list[float],
    list[float],
    list[float],
] | None:
    if not isinstance(bars, Sequence) or isinstance(
        bars,
        (str, bytes, bytearray),
    ):
        return None

    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    volumes: list[float] = []

    for bar in bars:
        if not isinstance(bar, Mapping):
            return None

        open_value = _finite(bar.get("open"))
        high_value = _finite(bar.get("high"))
        low_value = _finite(bar.get("low"))
        close_value = _finite(bar.get("close"))
        volume_value = _finite(bar.get("volume"))

        if any(
            value is None
            for value in (
                open_value,
                high_value,
                low_value,
                close_value,
                volume_value,
            )
        ):
            return None

        assert open_value is not None
        assert high_value is not None
        assert low_value is not None
        assert close_value is not None
        assert volume_value is not None

        if (
            open_value <= 0.0
            or high_value <= 0.0
            or low_value <= 0.0
            or close_value <= 0.0
            or volume_value < 0.0
            or high_value < low_value
            or high_value < max(open_value, close_value)
            or low_value > min(open_value, close_value)
        ):
            return None

        opens.append(open_value)
        highs.append(high_value)
        lows.append(low_value)
        closes.append(close_value)
        volumes.append(volume_value)

    return opens, highs, lows, closes, volumes


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _strength(
    numerator: float,
    denominator: float,
    *,
    scale: float = 1.0,
) -> float:
    if denominator <= 0.0:
        return 0.0

    return _clamp(
        abs(numerator)
        / denominator
        * scale
    )


def _result(
    contract: BulkIndicatorStrategyContractV3,
    decision: str,
    reason: str,
    confidence: float = 0.0,
    **evidence: object,
) -> dict[str, object]:
    bounded = (
        0.0
        if decision in ("HOLD", "ABSTAIN")
        else _clamp(confidence)
    )

    result: dict[str, object] = {
        "status":
            "abstain"
            if decision == "ABSTAIN"
            else "ok",
        "strategy_name": contract.strategy_name,
        "evaluator_id": contract.evaluator_id,
        "decision": decision,
        "signal": decision,
        "confidence": bounded,
        "reason": reason,
    }

    result.update(evidence)
    return result


def _abstain(
    contract: BulkIndicatorStrategyContractV3,
    reason: str,
) -> dict[str, object]:
    return _result(
        contract,
        "ABSTAIN",
        reason,
        0.0,
    )


def _direction(
    contract: BulkIndicatorStrategyContractV3,
    *,
    buy: bool,
    sell: bool,
    strength: float,
    evidence: Mapping[str, object],
) -> dict[str, object]:
    if buy and sell:
        return _abstain(
            contract,
            "simultaneous_directional_conditions",
        )

    if buy:
        return _result(
            contract,
            "BUY",
            "buy_condition_met",
            strength,
            **evidence,
        )

    if sell:
        return _result(
            contract,
            "SELL",
            "sell_condition_met",
            strength,
            **evidence,
        )

    return _result(
        contract,
        "HOLD",
        "no_directional_condition",
        0.0,
        **evidence,
    )


def _midpoint(
    highs: Sequence[float],
    lows: Sequence[float],
) -> float:
    return (
        max(highs)
        + min(lows)
    ) / 2.0


def _true_ranges(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
) -> list[float]:
    ranges = [
        highs[0] - lows[0]
    ]

    for index in range(1, len(closes)):
        ranges.append(
            max(
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
        )

    return ranges


def _rolling_atr(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
) -> list[float | None]:
    ranges = _true_ranges(
        closes,
        highs,
        lows,
    )

    output: list[float | None] = [
        None
    ] * len(ranges)

    if len(ranges) < window:
        return output

    current = fmean(
        ranges[:window]
    )

    output[window - 1] = current

    for index in range(
        window,
        len(ranges),
    ):
        current = (
            (
                current
                * (window - 1)
            )
            + ranges[index]
        ) / window

        output[index] = current

    return output


def _parabolic_sar(
    highs: Sequence[float],
    lows: Sequence[float],
    step: float,
    maximum: float,
) -> list[float]:
    bullish = (
        highs[1] + lows[1]
        >= highs[0] + lows[0]
    )

    sar = (
        lows[0]
        if bullish
        else highs[0]
    )

    extreme = (
        max(highs[0], highs[1])
        if bullish
        else min(lows[0], lows[1])
    )

    acceleration = step
    output = [sar, sar]

    for index in range(2, len(highs)):
        candidate = (
            sar
            + acceleration
            * (extreme - sar)
        )

        if bullish:
            candidate = min(
                candidate,
                lows[index - 1],
                lows[index - 2],
            )

            if lows[index] < candidate:
                bullish = False
                candidate = extreme
                extreme = lows[index]
                acceleration = step
            elif highs[index] > extreme:
                extreme = highs[index]
                acceleration = min(
                    maximum,
                    acceleration + step,
                )
        else:
            candidate = max(
                candidate,
                highs[index - 1],
                highs[index - 2],
            )

            if highs[index] > candidate:
                bullish = True
                candidate = extreme
                extreme = highs[index]
                acceleration = step
            elif lows[index] < extreme:
                extreme = lows[index]
                acceleration = min(
                    maximum,
                    acceleration + step,
                )

        sar = candidate
        output.append(sar)

    return output


def _aroon(
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
) -> tuple[float, float]:
    recent_highs = highs[-window:]
    recent_lows = lows[-window:]

    high_index = max(
        range(window),
        key=lambda index: (
            recent_highs[index],
            index,
        ),
    )

    low_index = min(
        range(window),
        key=lambda index: (
            recent_lows[index],
            -index,
        ),
    )

    periods_since_high = (
        window - 1 - high_index
    )

    periods_since_low = (
        window - 1 - low_index
    )

    divisor = max(1, window - 1)

    return (
        100.0
        * (
            divisor
            - periods_since_high
        )
        / divisor,
        100.0
        * (
            divisor
            - periods_since_low
        )
        / divisor,
    )


def _supertrend_directions(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    window: int,
    multiplier: float,
) -> tuple[
    list[int | None],
    list[float | None],
]:
    atr_values = _rolling_atr(
        closes,
        highs,
        lows,
        window,
    )

    directions: list[int | None] = [
        None
    ] * len(closes)

    bands: list[float | None] = [
        None
    ] * len(closes)

    final_upper: float | None = None
    final_lower: float | None = None
    direction = 1

    for index in range(
        window - 1,
        len(closes),
    ):
        atr_value = atr_values[index]

        if atr_value is None:
            continue

        midpoint = (
            highs[index]
            + lows[index]
        ) / 2.0

        basic_upper = (
            midpoint
            + multiplier * atr_value
        )

        basic_lower = (
            midpoint
            - multiplier * atr_value
        )

        if final_upper is None:
            final_upper = basic_upper
            final_lower = basic_lower
        else:
            previous_close = closes[index - 1]

            if (
                basic_upper < final_upper
                or previous_close > final_upper
            ):
                final_upper = basic_upper

            if (
                basic_lower > final_lower
                or previous_close < final_lower
            ):
                final_lower = basic_lower

        assert final_upper is not None
        assert final_lower is not None

        if direction < 0 and closes[index] > final_upper:
            direction = 1
        elif direction > 0 and closes[index] < final_lower:
            direction = -1

        directions[index] = direction
        bands[index] = (
            final_lower
            if direction > 0
            else final_upper
        )

    return directions, bands


def _zscore(
    values: Sequence[float],
) -> float | None:
    if not values:
        return None

    mean = fmean(values)

    variance = fmean(
        [
            (value - mean) ** 2
            for value in values
        ]
    )

    deviation = sqrt(variance)

    if deviation <= 0.0:
        return None

    return (
        values[-1] - mean
    ) / deviation


def _williams_r(
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    end: int,
    window: int,
) -> float | None:
    start = end - window + 1

    if start < 0:
        return None

    highest = max(
        highs[start:end + 1]
    )

    lowest = min(
        lows[start:end + 1]
    )

    spread = highest - lowest

    if spread <= 0.0:
        return None

    return (
        -100.0
        * (
            highest - closes[end]
        )
        / spread
    )


def _linear_regression(
    values: Sequence[float],
) -> tuple[float, float]:
    count = len(values)
    mean_x = (
        count - 1
    ) / 2.0
    mean_y = fmean(values)

    denominator = sum(
        (
            index - mean_x
        ) ** 2
        for index in range(count)
    )

    if denominator <= 0.0:
        return 0.0, mean_y

    slope = sum(
        (
            index - mean_x
        )
        * (
            value - mean_y
        )
        for index, value in enumerate(values)
    ) / denominator

    intercept = (
        mean_y
        - slope * mean_x
    )

    return slope, intercept


def _evaluate(
    contract: BulkIndicatorStrategyContractV3,
    bars: Sequence[Bar],
) -> dict[str, object]:
    extracted = _extract(bars)

    if extracted is None:
        return _abstain(
            contract,
            "invalid_truthful_daily_ohlcv",
        )

    opens, highs, lows, closes, volumes = extracted

    if len(closes) < contract.minimum_bars:
        return _abstain(
            contract,
            "insufficient_history",
        )

    name = contract.strategy_name
    parameters = contract.parameters

    if name == "Parabolic SAR Trend":
        values = _parabolic_sar(
            highs,
            lows,
            float(parameters["acceleration_step"]),
            float(parameters["acceleration_maximum"]),
        )

        previous_sar = values[-2]
        current_sar = values[-1]

        buy = (
            closes[-2] <= previous_sar
            and closes[-1] > current_sar
        )

        sell = (
            closes[-2] >= previous_sar
            and closes[-1] < current_sar
        )

        evidence = {
            "previous_sar": previous_sar,
            "current_sar": current_sar,
        }

        return _direction(
            contract,
            buy=buy,
            sell=sell,
            strength=_strength(
                closes[-1] - current_sar,
                closes[-1],
                scale=8.0,
            ),
            evidence=evidence,
        )

    if name == "Aroon Trend":
        up, down = _aroon(
            highs,
            lows,
            int(parameters["window"]),
        )

        trend = float(
            parameters["trend_threshold"]
        )

        opposite = float(
            parameters["opposite_threshold"]
        )

        return _direction(
            contract,
            buy=(
                up >= trend
                and down <= opposite
            ),
            sell=(
                down >= trend
                and up <= opposite
            ),
            strength=abs(up - down) / 100.0,
            evidence={
                "current_aroon_up": up,
                "current_aroon_down": down,
            },
        )

    if name == "Ichimoku Trend":
        conversion_window = int(
            parameters["conversion_window"]
        )

        base_window = int(
            parameters["base_window"]
        )

        span_b_window = int(
            parameters["span_b_window"]
        )

        displacement = int(
            parameters["displacement"]
        )

        conversion = _midpoint(
            highs[-conversion_window:],
            lows[-conversion_window:],
        )

        base = _midpoint(
            highs[-base_window:],
            lows[-base_window:],
        )

        cloud_end = (
            len(closes)
            - displacement
        )

        span_a_conversion = _midpoint(
            highs[
                cloud_end
                - conversion_window:
                cloud_end
            ],
            lows[
                cloud_end
                - conversion_window:
                cloud_end
            ],
        )

        span_a_base = _midpoint(
            highs[
                cloud_end
                - base_window:
                cloud_end
            ],
            lows[
                cloud_end
                - base_window:
                cloud_end
            ],
        )

        span_a = (
            span_a_conversion
            + span_a_base
        ) / 2.0

        span_b = _midpoint(
            highs[
                cloud_end
                - span_b_window:
                cloud_end
            ],
            lows[
                cloud_end
                - span_b_window:
                cloud_end
            ],
        )

        cloud_high = max(span_a, span_b)
        cloud_low = min(span_a, span_b)

        return _direction(
            contract,
            buy=(
                closes[-1] > cloud_high
                and conversion > base
            ),
            sell=(
                closes[-1] < cloud_low
                and conversion < base
            ),
            strength=_strength(
                closes[-1]
                - (
                    cloud_high
                    if closes[-1] > cloud_high
                    else cloud_low
                ),
                closes[-1],
                scale=5.0,
            ),
            evidence={
                "conversion_line": conversion,
                "base_line": base,
                "cloud_span_a": span_a,
                "cloud_span_b": span_b,
            },
        )

    if name == "Supertrend":
        directions, bands = _supertrend_directions(
            closes,
            highs,
            lows,
            int(parameters["atr_window"]),
            float(parameters["multiplier"]),
        )

        previous_direction = directions[-2]
        current_direction = directions[-1]
        current_band = bands[-1]

        if (
            previous_direction is None
            or current_direction is None
            or current_band is None
        ):
            return _abstain(
                contract,
                "supertrend_unavailable",
            )

        return _direction(
            contract,
            buy=(
                previous_direction < 0
                and current_direction > 0
            ),
            sell=(
                previous_direction > 0
                and current_direction < 0
            ),
            strength=_strength(
                closes[-1] - current_band,
                closes[-1],
                scale=5.0,
            ),
            evidence={
                "previous_supertrend_direction":
                    previous_direction,
                "current_supertrend_direction":
                    current_direction,
                "current_supertrend_band":
                    current_band,
            },
        )

    if name == "N-Day High Breakout":
        window = int(parameters["window"])

        prior_high = max(
            highs[-window - 1:-1]
        )

        prior_low = min(
            lows[-window - 1:-1]
        )

        return _direction(
            contract,
            buy=closes[-1] > prior_high,
            sell=closes[-1] < prior_low,
            strength=_strength(
                min(
                    abs(closes[-1] - prior_high),
                    abs(closes[-1] - prior_low),
                ),
                closes[-1],
                scale=10.0,
            ),
            evidence={
                "prior_window_high": prior_high,
                "prior_window_low": prior_low,
            },
        )

    if name == "N-Day Low Breakdown":
        window = int(parameters["window"])

        previous_boundary = min(
            lows[
                -window - 2:
                -2
            ]
        )

        current_boundary = min(
            lows[
                -window - 1:
                -1
            ]
        )

        previous_breakdown = (
            closes[-2]
            < previous_boundary
        )

        reclaimed = (
            closes[-1]
            > previous_boundary
        )

        current_breakdown = (
            closes[-1]
            < current_boundary
        )

        return _direction(
            contract,
            buy=(
                previous_breakdown
                and reclaimed
            ),
            sell=current_breakdown,
            strength=_strength(
                closes[-1] - current_boundary,
                closes[-1],
                scale=10.0,
            ),
            evidence={
                "previous_breakdown_boundary":
                    previous_boundary,
                "current_breakdown_boundary":
                    current_boundary,
                "previous_breakdown":
                    previous_breakdown,
            },
        )

    if name in (
        "NR4 Breakout",
        "NR7 Breakout",
    ):
        window = int(
            parameters["compression_window"]
        )

        candidate_index = len(closes) - 2

        start = (
            candidate_index
            - window
            + 1
        )

        ranges = [
            highs[index] - lows[index]
            for index in range(
                start,
                candidate_index + 1,
            )
        ]

        candidate_range = ranges[-1]

        narrowest = (
            candidate_range
            == min(ranges)
        )

        return _direction(
            contract,
            buy=(
                narrowest
                and closes[-1] > highs[-2]
            ),
            sell=(
                narrowest
                and closes[-1] < lows[-2]
            ),
            strength=_strength(
                closes[-1] - closes[-2],
                closes[-1],
                scale=10.0,
            ),
            evidence={
                "compression_window": window,
                "previous_range": candidate_range,
                "previous_is_narrowest":
                    narrowest,
                "previous_high": highs[-2],
                "previous_low": lows[-2],
            },
        )

    if name == "Inside Bar Breakout":
        inside = (
            highs[-2] <= highs[-3]
            and lows[-2] >= lows[-3]
        )

        return _direction(
            contract,
            buy=(
                inside
                and closes[-1] > highs[-3]
            ),
            sell=(
                inside
                and closes[-1] < lows[-3]
            ),
            strength=_strength(
                closes[-1] - closes[-2],
                closes[-1],
                scale=10.0,
            ),
            evidence={
                "inside_bar_confirmed": inside,
                "mother_bar_high": highs[-3],
                "mother_bar_low": lows[-3],
            },
        )

    if name == "Triangle Breakout":
        structure_window = int(
            parameters["structure_window"]
        )

        minimum_touches = int(
            parameters["minimum_touches"]
        )

        volume_window = int(
            parameters["volume_window"]
        )

        volume_multiplier = float(
            parameters["volume_multiplier"]
        )

        structure_highs = highs[
            -structure_window - 1:
            -1
        ]

        structure_lows = lows[
            -structure_window - 1:
            -1
        ]

        high_slope, high_intercept = (
            _linear_regression(
                structure_highs
            )
        )

        low_slope, low_intercept = (
            _linear_regression(
                structure_lows
            )
        )

        resistance = (
            high_intercept
            + high_slope
            * structure_window
        )

        support = (
            low_intercept
            + low_slope
            * structure_window
        )

        tolerance = max(
            closes[-1] * 0.01,
            1e-12,
        )

        high_touches = sum(
            abs(
                value
                - (
                    high_intercept
                    + high_slope * index
                )
            ) <= tolerance
            for index, value in enumerate(
                structure_highs
            )
        )

        low_touches = sum(
            abs(
                value
                - (
                    low_intercept
                    + low_slope * index
                )
            ) <= tolerance
            for index, value in enumerate(
                structure_lows
            )
        )

        converging = (
            high_slope < 0.0
            and low_slope > 0.0
            and resistance > support
            and high_touches >= minimum_touches
            and low_touches >= minimum_touches
        )

        average_volume = fmean(
            volumes[
                -volume_window - 1:
                -1
            ]
        )

        volume_confirmed = (
            average_volume > 0.0
            and volumes[-1]
            > average_volume
            * volume_multiplier
        )

        return _direction(
            contract,
            buy=(
                converging
                and volume_confirmed
                and closes[-1] > resistance
            ),
            sell=(
                converging
                and volume_confirmed
                and closes[-1] < support
            ),
            strength=_strength(
                closes[-1]
                - (
                    resistance
                    if closes[-1] > resistance
                    else support
                ),
                closes[-1],
                scale=10.0,
            ),
            evidence={
                "triangle_resistance":
                    resistance,
                "triangle_support":
                    support,
                "resistance_slope":
                    high_slope,
                "support_slope":
                    low_slope,
                "resistance_touches":
                    high_touches,
                "support_touches":
                    low_touches,
                "volume_confirmed":
                    volume_confirmed,
            },
        )

    if name == "Z-Score Mean Reversion":
        window = int(parameters["window"])
        entry = float(parameters["entry_z"])

        previous_z = _zscore(
            closes[
                -window - 1:
                -1
            ]
        )

        current_z = _zscore(
            closes[-window:]
        )

        if (
            previous_z is None
            or current_z is None
        ):
            return _result(
                contract,
                "HOLD",
                "zero_price_dispersion",
                0.0,
                previous_zscore=previous_z,
                current_zscore=current_z,
            )

        return _direction(
            contract,
            buy=(
                previous_z >= -entry
                and current_z < -entry
            ),
            sell=(
                previous_z <= entry
                and current_z > entry
            ),
            strength=min(
                1.0,
                abs(current_z) / 4.0,
            ),
            evidence={
                "previous_zscore": previous_z,
                "current_zscore": current_z,
            },
        )

    if name == "Williams %R Reversion":
        window = int(parameters["window"])

        previous_value = _williams_r(
            closes,
            highs,
            lows,
            len(closes) - 2,
            window,
        )

        current_value = _williams_r(
            closes,
            highs,
            lows,
            len(closes) - 1,
            window,
        )

        if (
            previous_value is None
            or current_value is None
        ):
            return _result(
                contract,
                "HOLD",
                "zero_price_range",
                0.0,
                previous_williams_r=previous_value,
                current_williams_r=current_value,
            )

        oversold = float(
            parameters["oversold_threshold"]
        )

        overbought = float(
            parameters["overbought_threshold"]
        )

        return _direction(
            contract,
            buy=(
                previous_value <= oversold
                and current_value > oversold
            ),
            sell=(
                previous_value >= overbought
                and current_value < overbought
            ),
            strength=min(
                1.0,
                abs(
                    current_value
                    - previous_value
                ) / 100.0,
            ),
            evidence={
                "previous_williams_r":
                    previous_value,
                "current_williams_r":
                    current_value,
            },
        )

    if name == "Gap Fade":
        threshold = float(
            parameters["minimum_gap_fraction"]
        )

        prior_close = closes[-2]

        gap_fraction = (
            opens[-1] - prior_close
        ) / prior_close

        return _direction(
            contract,
            buy=(
                gap_fraction <= -threshold
                and closes[-1] > opens[-1]
            ),
            sell=(
                gap_fraction >= threshold
                and closes[-1] < opens[-1]
            ),
            strength=min(
                1.0,
                abs(gap_fraction) * 10.0,
            ),
            evidence={
                "overnight_gap_fraction":
                    gap_fraction,
                "session_return_fraction":
                    (
                        closes[-1]
                        - opens[-1]
                    )
                    / opens[-1],
            },
        )

    if name == "Overnight Reversal":
        threshold = float(
            parameters[
                "minimum_overnight_return"
            ]
        )

        overnight_return = (
            opens[-1] - closes[-2]
        ) / closes[-2]

        session_return = (
            closes[-1] - opens[-1]
        ) / opens[-1]

        return _direction(
            contract,
            buy=(
                overnight_return <= -threshold
                and session_return > 0.0
            ),
            sell=(
                overnight_return >= threshold
                and session_return < 0.0
            ),
            strength=min(
                1.0,
                (
                    abs(overnight_return)
                    + abs(session_return)
                )
                * 5.0,
            ),
            evidence={
                "overnight_return":
                    overnight_return,
                "regular_session_return":
                    session_return,
            },
        )

    if name == "Short-Term Reversal Factor":
        window = int(
            parameters["return_window"]
        )

        threshold = float(
            parameters["reversal_threshold"]
        )

        base = closes[-window - 1]

        if base <= 0.0:
            return _abstain(
                contract,
                "zero_return_denominator",
            )

        trailing_return = (
            closes[-1] - base
        ) / base

        return _direction(
            contract,
            buy=trailing_return <= -threshold,
            sell=trailing_return >= threshold,
            strength=min(
                1.0,
                abs(trailing_return),
            ),
            evidence={
                "trailing_return":
                    trailing_return,
            },
        )

    return _abstain(
        contract,
        "unsupported_strategy_contract",
    )


def _make_evaluator(
    strategy_name: str,
) -> Evaluator:
    contract = (
        BULK_INDICATOR_STRATEGY_CONTRACTS_V3[
            strategy_name
        ]
    )

    def evaluator(
        bars: Sequence[Bar],
    ) -> dict[str, object]:
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
    evaluator.__doc__ = (
        "Evaluate "
        + contract.strategy_name
        + " using truthful daily OHLCV bars."
    )

    return evaluator


BULK_OFFLINE_EVALUATORS_V3 = MappingProxyType(
    {
        name: _make_evaluator(name)
        for name in BULK_INDICATOR_STRATEGY_CONTRACTS_V3
    }
)


def evaluate_bulk_indicator_strategy_v3(
    strategy_name: str,
    bars: Sequence[Bar],
) -> dict[str, object]:
    normalized = str(
        strategy_name
    ).strip()

    evaluator = BULK_OFFLINE_EVALUATORS_V3.get(
        normalized
    )

    if evaluator is None:
        raise KeyError(
            "No deterministic third-batch evaluator: "
            f"{normalized or '<empty>'}"
        )

    return evaluator(bars)


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_offline_evaluators_v3",
        "healthy": True,
        "evaluator_count": len(
            BULK_OFFLINE_EVALUATORS_V3
        ),
        "strategy_names": tuple(
            BULK_OFFLINE_EVALUATORS_V3
        ),
        "pure_functions": True,
        "provider_called": False,
        "database_accessed": False,
        "position_sizing_enabled": False,
        "portfolio_output_enabled": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }
