"""Pure deterministic indicator primitives for qualified evaluators."""

from __future__ import annotations

from math import isfinite, sqrt
from typing import Sequence


class IndicatorInputError(ValueError):
    """Indicator input violates the deterministic numeric contract."""


def _window(
    value: int,
) -> int:
    if (
        isinstance(value, bool)
        or
        not isinstance(value, int)
    ):
        raise IndicatorInputError(
            "window must be an integer"
        )

    if value <= 0:
        raise IndicatorInputError(
            "window must be greater than zero"
        )

    return value


def _finite_values(
    values: Sequence[float],
    *,
    label: str,
    positive: bool = False,
) -> list[float]:
    if isinstance(
        values,
        (
            str,
            bytes,
        ),
    ) or not isinstance(
        values,
        Sequence,
    ):
        raise IndicatorInputError(
            f"{label} must be a sequence"
        )

    result = []

    for index, raw in enumerate(
        values
    ):
        if isinstance(
            raw,
            bool,
        ):
            raise IndicatorInputError(
                f"{label}[{index}] must be numeric"
            )

        try:
            value = float(
                raw
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise IndicatorInputError(
                f"{label}[{index}] must be numeric"
            ) from exc

        if not isfinite(
            value
        ):
            raise IndicatorInputError(
                f"{label}[{index}] must be finite"
            )

        if (
            positive
            and
            value <= 0.0
        ):
            raise IndicatorInputError(
                f"{label}[{index}] must be greater than zero"
            )

        result.append(
            value
        )

    return result


def _equal_lengths(
    **series: list[float],
) -> None:
    lengths = {
        len(values)
        for values in series.values()
    }

    if len(lengths) > 1:
        raise IndicatorInputError(
            "indicator series must have equal lengths"
        )


def calculate_sma(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    clean = _finite_values(
        values,
        label="values",
    )

    period = _window(
        window
    )

    output: list[float | None] = [
        None
    ] * len(clean)

    if len(clean) < period:
        return output

    running = sum(
        clean[:period]
    )

    output[
        period - 1
    ] = running / period

    for index in range(
        period,
        len(clean),
    ):
        running += (
            clean[index]
            -
            clean[index - period]
        )

        output[index] = (
            running
            /
            period
        )

    return output


def calculate_ema(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    clean = _finite_values(
        values,
        label="values",
    )

    period = _window(
        window
    )

    output: list[float | None] = [
        None
    ] * len(clean)

    if len(clean) < period:
        return output

    seed = (
        sum(
            clean[:period]
        )
        /
        period
    )

    seed_index = period - 1
    output[seed_index] = seed

    alpha = 2.0 / (
        period + 1.0
    )

    previous = seed

    for index in range(
        period,
        len(clean),
    ):
        current = (
            alpha
            *
            clean[index]
            +
            (
                1.0
                -
                alpha
            )
            *
            previous
        )

        output[index] = current
        previous = current

    return output


def calculate_rolling_stddev(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    clean = _finite_values(
        values,
        label="values",
    )

    period = _window(
        window
    )

    output: list[float | None] = [
        None
    ] * len(clean)

    for index in range(
        period - 1,
        len(clean),
    ):
        sample = clean[
            index - period + 1:
            index + 1
        ]

        mean = sum(
            sample
        ) / period

        variance = sum(
            (
                value
                -
                mean
            ) ** 2
            for value in sample
        ) / period

        output[index] = sqrt(
            variance
        )

    return output


def calculate_true_range(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
) -> list[float]:
    high = _finite_values(
        highs,
        label="highs",
        positive=True,
    )

    low = _finite_values(
        lows,
        label="lows",
        positive=True,
    )

    close = _finite_values(
        closes,
        label="closes",
        positive=True,
    )

    _equal_lengths(
        highs=high,
        lows=low,
        closes=close,
    )

    output = []

    for index in range(
        len(close)
    ):
        if high[index] < low[index]:
            raise IndicatorInputError(
                f"highs[{index}] must be at least lows[{index}]"
            )

        if index == 0:
            value = (
                high[index]
                -
                low[index]
            )
        else:
            previous_close = close[
                index - 1
            ]

            value = max(
                high[index]
                -
                low[index],

                abs(
                    high[index]
                    -
                    previous_close
                ),

                abs(
                    low[index]
                    -
                    previous_close
                ),
            )

        output.append(
            value
        )

    return output


def calculate_atr(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    window: int = 14,
) -> list[float | None]:
    period = _window(
        window
    )

    true_range = calculate_true_range(
        highs,
        lows,
        closes,
    )

    output: list[float | None] = [
        None
    ] * len(true_range)

    if len(true_range) < period:
        return output

    previous = (
        sum(
            true_range[:period]
        )
        /
        period
    )

    output[
        period - 1
    ] = previous

    for index in range(
        period,
        len(true_range),
    ):
        current = (
            (
                previous
                *
                (
                    period - 1
                )
            )
            +
            true_range[index]
        ) / period

        output[index] = current
        previous = current

    return output


def calculate_bollinger_bands(
    values: Sequence[float],
    window: int = 20,
    multiplier: float = 2.0,
) -> dict[str, list[float | None]]:
    clean = _finite_values(
        values,
        label="values",
    )

    period = _window(
        window
    )

    if isinstance(
        multiplier,
        bool,
    ):
        raise IndicatorInputError(
            "multiplier must be numeric"
        )

    try:
        width = float(
            multiplier
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise IndicatorInputError(
            "multiplier must be numeric"
        ) from exc

    if (
        not isfinite(width)
        or
        width < 0.0
    ):
        raise IndicatorInputError(
            "multiplier must be finite and non-negative"
        )

    middle = calculate_sma(
        clean,
        period,
    )

    deviation = calculate_rolling_stddev(
        clean,
        period,
    )

    upper: list[float | None] = [
        None
    ] * len(clean)

    lower: list[float | None] = [
        None
    ] * len(clean)

    for index in range(
        len(clean)
    ):
        mean = middle[index]
        stddev = deviation[index]

        if (
            mean is None
            or
            stddev is None
        ):
            continue

        upper[index] = (
            mean
            +
            width
            *
            stddev
        )

        lower[index] = (
            mean
            -
            width
            *
            stddev
        )

    return {
        "middle":
            middle,

        "upper":
            upper,

        "lower":
            lower,

        "stddev":
            deviation,
    }


def calculate_rsi(
    closes: Sequence[float],
    window: int = 14,
) -> list[float | None]:
    close = _finite_values(
        closes,
        label="closes",
        positive=True,
    )

    period = _window(
        window
    )

    output: list[float | None] = [
        None
    ] * len(close)

    if len(close) <= period:
        return output

    changes = [
        close[index]
        -
        close[index - 1]
        for index in range(
            1,
            len(close),
        )
    ]

    gains = [
        max(
            change,
            0.0,
        )
        for change in changes
    ]

    losses = [
        max(
            -change,
            0.0,
        )
        for change in changes
    ]

    average_gain = (
        sum(
            gains[:period]
        )
        /
        period
    )

    average_loss = (
        sum(
            losses[:period]
        )
        /
        period
    )

    def rsi_value() -> float:
        if (
            average_gain == 0.0
            and
            average_loss == 0.0
        ):
            return 50.0

        if average_loss == 0.0:
            return 100.0

        if average_gain == 0.0:
            return 0.0

        relative_strength = (
            average_gain
            /
            average_loss
        )

        return 100.0 - (
            100.0
            /
            (
                1.0
                +
                relative_strength
            )
        )

    output[period] = rsi_value()

    for close_index in range(
        period + 1,
        len(close),
    ):
        change_index = (
            close_index - 1
        )

        average_gain = (
            (
                average_gain
                *
                (
                    period - 1
                )
            )
            +
            gains[change_index]
        ) / period

        average_loss = (
            (
                average_loss
                *
                (
                    period - 1
                )
            )
            +
            losses[change_index]
        ) / period

        output[
            close_index
        ] = rsi_value()

    return output


def calculate_donchian_channels(
    highs: Sequence[float],
    lows: Sequence[float],
    window: int = 20,
) -> dict[str, list[float | None]]:
    high = _finite_values(
        highs,
        label="highs",
        positive=True,
    )

    low = _finite_values(
        lows,
        label="lows",
        positive=True,
    )

    _equal_lengths(
        highs=high,
        lows=low,
    )

    period = _window(
        window
    )

    upper: list[float | None] = [
        None
    ] * len(high)

    lower: list[float | None] = [
        None
    ] * len(high)

    middle: list[float | None] = [
        None
    ] * len(high)

    for index in range(
        len(high)
    ):
        if high[index] < low[index]:
            raise IndicatorInputError(
                f"highs[{index}] must be at least lows[{index}]"
            )

    for index in range(
        period - 1,
        len(high),
    ):
        start = (
            index - period + 1
        )

        current_upper = max(
            high[
                start:
                index + 1
            ]
        )

        current_lower = min(
            low[
                start:
                index + 1
            ]
        )

        upper[index] = current_upper
        lower[index] = current_lower
        middle[index] = (
            current_upper
            +
            current_lower
        ) / 2.0

    return {
        "upper":
            upper,

        "lower":
            lower,

        "middle":
            middle,
    }


def calculate_cci(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    window: int = 20,
) -> list[float | None]:
    high = _finite_values(
        highs,
        label="highs",
        positive=True,
    )

    low = _finite_values(
        lows,
        label="lows",
        positive=True,
    )

    close = _finite_values(
        closes,
        label="closes",
        positive=True,
    )

    _equal_lengths(
        highs=high,
        lows=low,
        closes=close,
    )

    period = _window(
        window
    )

    for index in range(
        len(close)
    ):
        if high[index] < low[index]:
            raise IndicatorInputError(
                f"highs[{index}] must be at least lows[{index}]"
            )

    typical = [
        (
            high[index]
            +
            low[index]
            +
            close[index]
        ) / 3.0
        for index in range(
            len(close)
        )
    ]

    output: list[float | None] = [
        None
    ] * len(typical)

    for index in range(
        period - 1,
        len(typical),
    ):
        sample = typical[
            index - period + 1:
            index + 1
        ]

        mean = sum(
            sample
        ) / period

        mean_deviation = sum(
            abs(
                value
                -
                mean
            )
            for value in sample
        ) / period

        if mean_deviation == 0.0:
            output[index] = 0.0
        else:
            output[index] = (
                typical[index]
                -
                mean
            ) / (
                0.015
                *
                mean_deviation
            )

    return output


def calculate_trix(
    values: Sequence[float],
    window: int = 15,
) -> list[float | None]:
    clean = _finite_values(
        values,
        label="values",
        positive=True,
    )

    period = _window(
        window
    )

    output: list[float | None] = [
        None
    ] * len(clean)

    ema_one = calculate_ema(
        clean,
        period,
    )

    first_values = [
        value
        for value in ema_one
        if value is not None
    ]

    if len(first_values) < period:
        return output

    ema_two_compact = calculate_ema(
        first_values,
        period,
    )

    second_values = [
        value
        for value in ema_two_compact
        if value is not None
    ]

    if len(second_values) < period:
        return output

    ema_three_compact = calculate_ema(
        second_values,
        period,
    )

    third_values = [
        value
        for value in ema_three_compact
        if value is not None
    ]

    if len(third_values) < 2:
        return output

    first_third_index = (
        3
        *
        (
            period - 1
        )
    )

    for compact_index in range(
        1,
        len(third_values),
    ):
        previous = third_values[
            compact_index - 1
        ]

        current = third_values[
            compact_index
        ]

        output_index = (
            first_third_index
            +
            compact_index
        )

        output[output_index] = (
            (
                current
                -
                previous
            )
            /
            previous
        ) * 100.0

    return output


def healthcheck() -> dict[str, object]:
    return {
        "component":
            "deterministic_indicator_primitives_v1",

        "healthy":
            True,

        "primitives": (
            "sma",
            "ema",
            "rolling_stddev",
            "true_range",
            "atr",
            "bollinger_bands",
            "rsi",
            "donchian_channels",
            "cci",
            "trix",
        ),

        "pure_math_only":
            True,

        "provider_called":
            False,

        "database_accessed":
            False,

        "execution_enabled":
            False,
    }
