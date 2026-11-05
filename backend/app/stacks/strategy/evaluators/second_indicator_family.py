"""Pure deterministic evaluators for the second indicator family."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
    Sequence,
)
from math import isfinite
from types import MappingProxyType

from backend.app.stacks.strategy.evaluators.indicators import (
    IndicatorInputError,
    calculate_atr,
    calculate_donchian_channels,
    calculate_ema,
)
from backend.app.stacks.strategy.evaluators.second_indicator_strategy_contracts import (
    ATR_VOLATILITY_BREAKOUT,
    DONCHIAN_CHANNEL_BREAKOUT,
    KELTNER_CHANNEL_BREAKOUT,
    SECOND_INDICATOR_STRATEGY_CONTRACTS,
    VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
    SecondIndicatorStrategyContract,
)


class SecondIndicatorFamilyInputError(ValueError):
    """Raised when truthful OHLC input is malformed."""


def _abstain(
    contract: SecondIndicatorStrategyContract,
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
        "transition_only": contract.transition_only,
    }

    if error:
        result[
            "error"
        ] = error

    return result


def _result(
    contract: SecondIndicatorStrategyContract,
    *,
    decision: str,
    confidence: float,
    reason: str,
    received_bars: int,
    evidence: Mapping[str, object],
) -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_name": contract.strategy_name,
        "evaluator_id": contract.evaluator_id,
        "decision": decision,
        "signal": decision,
        "confidence": min(
            max(
                float(
                    confidence
                ),
                0.0,
            ),
            1.0,
        ),
        "reason": reason,
        "received_bars": received_bars,
        "minimum_bars": contract.minimum_bars,
        "transition_only": contract.transition_only,
        **dict(
            evidence
        ),
    }


def _received(
    bars: object,
) -> int:
    try:
        return len(
            bars
        )
    except TypeError:
        return 0


def _extract_ohlc(
    bars: Sequence[object],
) -> tuple[
    list[float],
    list[float],
    list[float],
]:
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
        raise SecondIndicatorFamilyInputError(
            "bars must be a sequence"
        )

    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []

    for index, raw_bar in enumerate(
        bars
    ):
        if not isinstance(
            raw_bar,
            Mapping,
        ):
            raise SecondIndicatorFamilyInputError(
                f"bars[{index}] must be a mapping"
            )

        values: dict[str, float] = {}

        for field in (
            "high",
            "low",
            "close",
        ):
            raw_value = raw_bar.get(
                field
            )

            if isinstance(
                raw_value,
                bool,
            ):
                raise SecondIndicatorFamilyInputError(
                    f"bars[{index}].{field} must be numeric"
                )

            try:
                value = float(
                    raw_value
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SecondIndicatorFamilyInputError(
                    f"bars[{index}].{field} must be numeric"
                ) from exc

            if (
                not isfinite(
                    value
                )
                or
                value <= 0.0
            ):
                raise SecondIndicatorFamilyInputError(
                    f"bars[{index}].{field} must be finite and greater than zero"
                )

            values[
                field
            ] = value

        if values[
            "high"
        ] < values[
            "low"
        ]:
            raise SecondIndicatorFamilyInputError(
                f"bars[{index}].high must be at least low"
            )

        if not (
            values[
                "low"
            ]
            <=
            values[
                "close"
            ]
            <=
            values[
                "high"
            ]
        ):
            raise SecondIndicatorFamilyInputError(
                f"bars[{index}].close must be within high and low"
            )

        highs.append(
            values[
                "high"
            ]
        )

        lows.append(
            values[
                "low"
            ]
        )

        closes.append(
            values[
                "close"
            ]
        )

    return (
        highs,
        lows,
        closes,
    )


def _confidence(
    value: float,
    boundary: float,
) -> float:
    return min(
        abs(
            value
            -
            boundary
        )
        /
        max(
            abs(
                boundary
            ),
            1e-12,
        ),
        1.0,
    )


def evaluate_donchian_channel_breakout(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = DONCHIAN_CHANNEL_BREAKOUT
    received = _received(
        bars
    )

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    if contract.channel_window is None:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_parameter_contract",
        )

    try:
        highs, lows, closes = _extract_ohlc(
            bars
        )

        channels = calculate_donchian_channels(
            highs[
                :-1
            ],
            lows[
                :-1
            ],
            window=contract.channel_window,
        )

        previous_upper = channels[
            "upper"
        ][-2]

        previous_lower = channels[
            "lower"
        ][-2]

        current_upper = channels[
            "upper"
        ][-1]

        current_lower = channels[
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
            raise SecondIndicatorFamilyInputError(
                "Donchian values are unavailable after warm-up"
            )

        previous_upper = float(
            previous_upper
        )

        previous_lower = float(
            previous_lower
        )

        current_upper = float(
            current_upper
        )

        current_lower = float(
            current_lower
        )

    except (
        IndicatorInputError,
        SecondIndicatorFamilyInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(
                exc
            ),
        )

    buy = (
        closes[
            -2
        ] <= previous_upper
        and
        closes[
            -1
        ] > current_upper
    )

    sell = (
        closes[
            -2
        ] >= previous_lower
        and
        closes[
            -1
        ] < current_lower
    )

    if buy and sell:
        return _abstain(
            contract,
            received_bars=received,
            reason="ambiguous_dual_trigger",
        )

    if buy:
        decision = "BUY"
        reason = "close_crossed_above_prior_donchian_channel"
        confidence = _confidence(
            closes[
                -1
            ],
            current_upper,
        )

    elif sell:
        decision = "SELL"
        reason = "close_crossed_below_prior_donchian_channel"
        confidence = _confidence(
            closes[
                -1
            ],
            current_lower,
        )

    else:
        decision = "HOLD"
        reason = "no_new_donchian_breakout"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "channel_window":
                contract.channel_window,

            "previous_close":
                closes[
                    -2
                ],

            "current_close":
                closes[
                    -1
                ],

            "previous_upper_channel":
                previous_upper,

            "previous_lower_channel":
                previous_lower,

            "current_upper_channel":
                current_upper,

            "current_lower_channel":
                current_lower,
        },
    )


def _atr_transition_values(
    bars: Sequence[object],
    contract: SecondIndicatorStrategyContract,
) -> tuple[
    list[float],
    list[float],
    list[float],
    float,
    float,
]:
    if (
        contract.atr_window is None
        or
        contract.atr_multiplier is None
    ):
        raise SecondIndicatorFamilyInputError(
            "ATR parameter contract is unavailable"
        )

    highs, lows, closes = _extract_ohlc(
        bars
    )

    atr = calculate_atr(
        highs,
        lows,
        closes,
        window=contract.atr_window,
    )

    previous_atr = atr[
        -2
    ]

    current_atr = atr[
        -1
    ]

    if (
        previous_atr is None
        or
        current_atr is None
    ):
        raise SecondIndicatorFamilyInputError(
            "ATR values are unavailable after warm-up"
        )

    return (
        highs,
        lows,
        closes,
        float(
            previous_atr
        ),
        float(
            current_atr
        ),
    )


def evaluate_atr_volatility_breakout(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = ATR_VOLATILITY_BREAKOUT
    received = _received(
        bars
    )

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    try:
        (
            _,
            _,
            closes,
            previous_atr,
            current_atr,
        ) = _atr_transition_values(
            bars,
            contract,
        )

        multiplier = float(
            contract.atr_multiplier
        )

        previous_reference = closes[
            -3
        ]

        current_reference = closes[
            -2
        ]

        previous_upper = (
            previous_reference
            +
            multiplier
            *
            previous_atr
        )

        previous_lower = (
            previous_reference
            -
            multiplier
            *
            previous_atr
        )

        current_upper = (
            current_reference
            +
            multiplier
            *
            current_atr
        )

        current_lower = (
            current_reference
            -
            multiplier
            *
            current_atr
        )

    except (
        IndicatorInputError,
        SecondIndicatorFamilyInputError,
        IndexError,
        TypeError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(
                exc
            ),
        )

    buy = (
        closes[
            -2
        ] <= previous_upper
        and
        closes[
            -1
        ] > current_upper
    )

    sell = (
        closes[
            -2
        ] >= previous_lower
        and
        closes[
            -1
        ] < current_lower
    )

    if buy and sell:
        return _abstain(
            contract,
            received_bars=received,
            reason="ambiguous_dual_trigger",
        )

    if buy:
        decision = "BUY"
        reason = "close_crossed_above_atr_breakout_level"
        confidence = _confidence(
            closes[
                -1
            ],
            current_upper,
        )

    elif sell:
        decision = "SELL"
        reason = "close_crossed_below_atr_breakout_level"
        confidence = _confidence(
            closes[
                -1
            ],
            current_lower,
        )

    else:
        decision = "HOLD"
        reason = "no_new_atr_volatility_breakout"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "atr_window":
                contract.atr_window,

            "atr_multiplier":
                contract.atr_multiplier,

            "previous_close":
                closes[
                    -2
                ],

            "current_close":
                closes[
                    -1
                ],

            "previous_atr":
                previous_atr,

            "current_atr":
                current_atr,

            "previous_upper_trigger":
                previous_upper,

            "previous_lower_trigger":
                previous_lower,

            "current_upper_trigger":
                current_upper,

            "current_lower_trigger":
                current_lower,
        },
    )


def evaluate_keltner_channel_breakout(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = KELTNER_CHANNEL_BREAKOUT
    received = _received(
        bars
    )

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    if (
        contract.ema_window is None
        or
        contract.atr_window is None
        or
        contract.atr_multiplier is None
    ):
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_parameter_contract",
        )

    try:
        highs, lows, closes = _extract_ohlc(
            bars
        )

        ema = calculate_ema(
            closes,
            window=contract.ema_window,
        )

        atr = calculate_atr(
            highs,
            lows,
            closes,
            window=contract.atr_window,
        )

        previous_ema = ema[
            -2
        ]

        current_ema = ema[
            -1
        ]

        previous_atr = atr[
            -2
        ]

        current_atr = atr[
            -1
        ]

        if any(
            value is None
            for value in (
                previous_ema,
                current_ema,
                previous_atr,
                current_atr,
            )
        ):
            raise SecondIndicatorFamilyInputError(
                "Keltner values are unavailable after warm-up"
            )

        multiplier = float(
            contract.atr_multiplier
        )

        previous_upper = (
            float(
                previous_ema
            )
            +
            multiplier
            *
            float(
                previous_atr
            )
        )

        previous_lower = (
            float(
                previous_ema
            )
            -
            multiplier
            *
            float(
                previous_atr
            )
        )

        current_upper = (
            float(
                current_ema
            )
            +
            multiplier
            *
            float(
                current_atr
            )
        )

        current_lower = (
            float(
                current_ema
            )
            -
            multiplier
            *
            float(
                current_atr
            )
        )

    except (
        IndicatorInputError,
        SecondIndicatorFamilyInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(
                exc
            ),
        )

    buy = (
        closes[
            -2
        ] <= previous_upper
        and
        closes[
            -1
        ] > current_upper
    )

    sell = (
        closes[
            -2
        ] >= previous_lower
        and
        closes[
            -1
        ] < current_lower
    )

    if buy and sell:
        return _abstain(
            contract,
            received_bars=received,
            reason="ambiguous_dual_trigger",
        )

    if buy:
        decision = "BUY"
        reason = "close_crossed_above_upper_keltner_band"
        confidence = _confidence(
            closes[
                -1
            ],
            current_upper,
        )

    elif sell:
        decision = "SELL"
        reason = "close_crossed_below_lower_keltner_band"
        confidence = _confidence(
            closes[
                -1
            ],
            current_lower,
        )

    else:
        decision = "HOLD"
        reason = "no_new_keltner_breakout"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "ema_window":
                contract.ema_window,

            "atr_window":
                contract.atr_window,

            "atr_multiplier":
                contract.atr_multiplier,

            "previous_close":
                closes[
                    -2
                ],

            "current_close":
                closes[
                    -1
                ],

            "previous_middle":
                float(
                    previous_ema
                ),

            "current_middle":
                float(
                    current_ema
                ),

            "previous_atr":
                float(
                    previous_atr
                ),

            "current_atr":
                float(
                    current_atr
                ),

            "previous_upper_band":
                previous_upper,

            "previous_lower_band":
                previous_lower,

            "current_upper_band":
                current_upper,

            "current_lower_band":
                current_lower,
        },
    )


def evaluate_volatility_breakout_from_previous_close(
    bars: Sequence[object],
) -> dict[str, object]:
    contract = (
        VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE
    )

    received = _received(
        bars
    )

    if received < contract.minimum_bars:
        return _abstain(
            contract,
            received_bars=received,
            reason="insufficient_truthful_bars",
        )

    if (
        contract.atr_window is None
        or
        contract.atr_multiplier is None
    ):
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_parameter_contract",
        )

    try:
        highs, lows, closes = _extract_ohlc(
            bars
        )

        atr = calculate_atr(
            highs,
            lows,
            closes,
            window=contract.atr_window,
        )

        current_atr = atr[
            -1
        ]

        if current_atr is None:
            raise SecondIndicatorFamilyInputError(
                "ATR value is unavailable after warm-up"
            )

        current_atr = float(
            current_atr
        )

        previous_close = closes[
            -2
        ]

        multiplier = float(
            contract.atr_multiplier
        )

        long_trigger = (
            previous_close
            +
            multiplier
            *
            current_atr
        )

        short_trigger = (
            previous_close
            -
            multiplier
            *
            current_atr
        )

    except (
        IndicatorInputError,
        SecondIndicatorFamilyInputError,
        IndexError,
    ) as exc:
        return _abstain(
            contract,
            received_bars=received,
            reason="invalid_truthful_bars",
            error=str(
                exc
            ),
        )

    long_reached = highs[
        -1
    ] >= long_trigger

    short_reached = lows[
        -1
    ] <= short_trigger

    if (
        long_reached
        and
        short_reached
    ):
        return _abstain(
            contract,
            received_bars=received,
            reason="ambiguous_dual_trigger",
        )

    if long_reached:
        decision = "BUY"
        reason = "daily_high_reached_previous_close_atr_trigger"
        confidence = _confidence(
            highs[
                -1
            ],
            long_trigger,
        )

    elif short_reached:
        decision = "SELL"
        reason = "daily_low_reached_previous_close_atr_trigger"
        confidence = _confidence(
            lows[
                -1
            ],
            short_trigger,
        )

    else:
        decision = "HOLD"
        reason = "no_previous_close_atr_trigger_reached"
        confidence = 0.0

    return _result(
        contract,
        decision=decision,
        confidence=confidence,
        reason=reason,
        received_bars=received,
        evidence={
            "atr_window":
                contract.atr_window,

            "atr_multiplier":
                contract.atr_multiplier,

            "previous_close":
                previous_close,

            "current_high":
                highs[
                    -1
                ],

            "current_low":
                lows[
                    -1
                ],

            "current_close":
                closes[
                    -1
                ],

            "current_atr":
                current_atr,

            "long_trigger":
                long_trigger,

            "short_trigger":
                short_trigger,

            "long_trigger_reached":
                long_reached,

            "short_trigger_reached":
                short_reached,
        },
    )


OfflineEvaluator = Callable[
    [Sequence[object]],
    dict[str, object],
]


OFFLINE_SECOND_INDICATOR_EVALUATORS = (
    MappingProxyType(
        {
            DONCHIAN_CHANNEL_BREAKOUT.strategy_name:
                evaluate_donchian_channel_breakout,

            ATR_VOLATILITY_BREAKOUT.strategy_name:
                evaluate_atr_volatility_breakout,

            KELTNER_CHANNEL_BREAKOUT.strategy_name:
                evaluate_keltner_channel_breakout,

            VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE.strategy_name:
                evaluate_volatility_breakout_from_previous_close,
        }
    )
)


def evaluate_offline_second_indicator_strategy(
    strategy_name: str,
    bars: Sequence[object],
) -> dict[str, object]:
    normalized_name = str(
        strategy_name
    ).strip()

    evaluator = (
        OFFLINE_SECOND_INDICATOR_EVALUATORS.get(
            normalized_name
        )
    )

    if evaluator is None:
        raise KeyError(
            "No offline-qualified second-family evaluator: "
            f"{normalized_name or '<empty>'}"
        )

    return evaluator(
        bars
    )


def healthcheck() -> dict[str, object]:
    return {
        "component":
            "second_indicator_family_evaluators_v1",

        "healthy":
            True,

        "offline_evaluator_count":
            len(
                OFFLINE_SECOND_INDICATOR_EVALUATORS
            ),

        "strategy_names":
            tuple(
                OFFLINE_SECOND_INDICATOR_EVALUATORS
            ),

        "contract_names":
            tuple(
                SECOND_INDICATOR_STRATEGY_CONTRACTS
            ),

        "truthful_ohlc_validation":
            True,

        "dual_trigger_fails_closed":
            True,

        "active_registry_modified":
            False,

        "aggregation_modified":
            False,

        "owner_decision_integrated":
            False,

        "provider_called":
            False,

        "database_accessed":
            False,

        "execution_enabled":
            False,
    }
