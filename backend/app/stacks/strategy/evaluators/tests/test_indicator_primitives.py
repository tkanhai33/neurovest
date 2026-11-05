from math import sqrt

import pytest

from backend.app.stacks.strategy.evaluators.indicators import (
    IndicatorInputError,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_cci,
    calculate_donchian_channels,
    calculate_ema,
    calculate_rolling_stddev,
    calculate_rsi,
    calculate_sma,
    calculate_trix,
    calculate_true_range,
    healthcheck,
)


def test_sma_has_explicit_warmup_and_exact_values():
    assert calculate_sma(
        [
            1.0,
            2.0,
            3.0,
        ],
        2,
    ) == [
        None,
        1.5,
        2.5,
    ]


def test_ema_uses_sma_seed_and_standard_alpha():
    assert calculate_ema(
        [
            1.0,
            2.0,
            3.0,
            4.0,
        ],
        3,
    ) == [
        None,
        None,
        2.0,
        3.0,
    ]


def test_population_rolling_standard_deviation():
    result = calculate_rolling_stddev(
        [
            1.0,
            2.0,
            3.0,
        ],
        3,
    )

    assert result[:2] == [
        None,
        None,
    ]

    assert result[2] == pytest.approx(
        sqrt(
            2.0 / 3.0
        )
    )


def test_true_range_includes_previous_close_gap():
    assert calculate_true_range(
        [
            10.0,
            12.0,
        ],
        [
            8.0,
            9.0,
        ],
        [
            9.0,
            11.0,
        ],
    ) == [
        2.0,
        3.0,
    ]


def test_atr_uses_wilder_smoothing():
    result = calculate_atr(
        [
            10.0,
            12.0,
            13.0,
        ],
        [
            8.0,
            9.0,
            10.0,
        ],
        [
            9.0,
            11.0,
            12.0,
        ],
        window=2,
    )

    assert result == [
        None,
        2.5,
        2.75,
    ]


def test_bollinger_bands_are_exact_population_bands():
    result = calculate_bollinger_bands(
        [
            1.0,
            2.0,
            3.0,
        ],
        window=3,
        multiplier=2.0,
    )

    deviation = sqrt(
        2.0 / 3.0
    )

    assert result[
        "middle"
    ][2] == 2.0

    assert result[
        "upper"
    ][2] == pytest.approx(
        2.0
        +
        2.0
        *
        deviation
    )

    assert result[
        "lower"
    ][2] == pytest.approx(
        2.0
        -
        2.0
        *
        deviation
    )


def test_rsi_rising_falling_and_flat_contracts():
    rising = calculate_rsi(
        [
            1.0,
            2.0,
            3.0,
            4.0,
        ],
        window=3,
    )

    falling = calculate_rsi(
        [
            4.0,
            3.0,
            2.0,
            1.0,
        ],
        window=3,
    )

    flat = calculate_rsi(
        [
            2.0,
            2.0,
            2.0,
            2.0,
        ],
        window=3,
    )

    assert rising[-1] == 100.0
    assert falling[-1] == 0.0
    assert flat[-1] == 50.0


def test_donchian_channels_use_exact_rolling_extremes():
    result = calculate_donchian_channels(
        [
            10.0,
            12.0,
            11.0,
        ],
        [
            8.0,
            9.0,
            7.0,
        ],
        window=2,
    )

    assert result[
        "upper"
    ] == [
        None,
        12.0,
        12.0,
    ]

    assert result[
        "lower"
    ] == [
        None,
        8.0,
        7.0,
    ]

    assert result[
        "middle"
    ] == [
        None,
        10.0,
        9.5,
    ]


def test_cci_flat_market_is_zero_after_warmup():
    result = calculate_cci(
        [
            10.0,
            10.0,
            10.0,
        ],
        [
            10.0,
            10.0,
            10.0,
        ],
        [
            10.0,
            10.0,
            10.0,
        ],
        window=3,
    )

    assert result == [
        None,
        None,
        0.0,
    ]


def test_trix_is_deterministic_and_positive_for_rising_series():
    values = [
        100.0
        +
        index
        for index in range(
            40
        )
    ]

    first = calculate_trix(
        values,
        window=5,
    )

    second = calculate_trix(
        values,
        window=5,
    )

    assert first == second

    populated = [
        value
        for value in first
        if value is not None
    ]

    assert populated
    assert all(
        value > 0.0
        for value in populated
    )


@pytest.mark.parametrize(
    "function,args",
    [
        (
            calculate_sma,
            (
                [1.0],
                0,
            ),
        ),
        (
            calculate_ema,
            (
                [1.0],
                True,
            ),
        ),
        (
            calculate_rolling_stddev,
            (
                [1.0],
                -1,
            ),
        ),
        (
            calculate_rsi,
            (
                [1.0],
                0,
            ),
        ),
    ],
)
def test_invalid_windows_fail_closed(
    function,
    args,
):
    with pytest.raises(
        IndicatorInputError
    ):
        function(
            *args
        )


@pytest.mark.parametrize(
    "bad_value",
    [
        None,
        True,
        "not-a-number",
        float("nan"),
        float("inf"),
    ],
)
def test_invalid_numeric_values_fail_closed(
    bad_value,
):
    with pytest.raises(
        IndicatorInputError
    ):
        calculate_sma(
            [
                1.0,
                bad_value,
            ],
            2,
        )


def test_mismatched_ohlc_lengths_fail_closed():
    with pytest.raises(
        IndicatorInputError
    ):
        calculate_true_range(
            [
                10.0,
                11.0,
            ],
            [
                9.0,
            ],
            [
                9.5,
                10.5,
            ],
        )


def test_high_below_low_fails_closed():
    with pytest.raises(
        IndicatorInputError
    ):
        calculate_true_range(
            [
                8.0,
            ],
            [
                9.0,
            ],
            [
                8.5,
            ],
        )


def test_healthcheck_is_side_effect_free():
    result = healthcheck()

    assert result[
        "healthy"
    ] is True

    assert result[
        "pure_math_only"
    ] is True

    assert result[
        "provider_called"
    ] is False

    assert result[
        "database_accessed"
    ] is False

    assert result[
        "execution_enabled"
    ] is False

    assert len(
        result[
            "primitives"
        ]
    ) == 10
