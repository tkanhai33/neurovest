"""Static exact-name evaluator allowlist."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from types import MappingProxyType
from typing import Any

from backend.app.stacks.strategy.evaluators.indicator_family import (
    evaluate_bollinger_band_breakout,
    evaluate_bollinger_band_mean_reversion,
    evaluate_rsi_overbought_mean_reversion,
    evaluate_rsi_oversold_mean_reversion,
)
from backend.app.stacks.strategy.evaluators.indicator_strategy_contracts import (
    BOLLINGER_BREAKOUT,
    BOLLINGER_MEAN_REVERSION,
    RSI_OVERBOUGHT_MEAN_REVERSION,
    RSI_OVERSOLD_MEAN_REVERSION,
)
from backend.app.stacks.strategy.evaluators.second_indicator_family import (
    evaluate_atr_volatility_breakout,
    evaluate_donchian_channel_breakout,
    evaluate_keltner_channel_breakout,
    evaluate_volatility_breakout_from_previous_close,
)
from backend.app.stacks.strategy.evaluators.second_indicator_strategy_contracts import (
    ATR_VOLATILITY_BREAKOUT,
    DONCHIAN_CHANNEL_BREAKOUT,
    KELTNER_CHANNEL_BREAKOUT,
    VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
)
from backend.app.stacks.strategy.evaluators.sma_crossover import (
    STRATEGY_NAME,
    evaluate_sma_crossover,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family import (
    BULK_OFFLINE_EVALUATORS,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v2 import (
    BULK_OFFLINE_EVALUATORS_V2,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    BULK_OFFLINE_EVALUATORS_V3,
)


class UnsupportedStrategyEvaluatorError(
    LookupError
):
    """The requested catalog strategy has no qualified evaluator."""


Evaluator = Callable[
    [
        Sequence[
            dict[str, Any]
        ]
    ],
    dict[str, Any],
]


_ORIGINAL_NINE_EVALUATORS = MappingProxyType(
    {
        STRATEGY_NAME:
            evaluate_sma_crossover,

        BOLLINGER_BREAKOUT.strategy_name:
            evaluate_bollinger_band_breakout,

        BOLLINGER_MEAN_REVERSION.strategy_name:
            evaluate_bollinger_band_mean_reversion,

        RSI_OVERBOUGHT_MEAN_REVERSION.strategy_name:
            evaluate_rsi_overbought_mean_reversion,

        RSI_OVERSOLD_MEAN_REVERSION.strategy_name:
            evaluate_rsi_oversold_mean_reversion,

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

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **_ORIGINAL_NINE_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V2,
        **BULK_OFFLINE_EVALUATORS_V3,
    }
)


def evaluate_allowlisted_strategy(
    strategy_name: str,
    bars: Sequence[dict[str, Any]],
    *,
    primary_symbol: str | None = None,
    universe_bars: object = None,
) -> dict[str, Any]:
    normalized_name = str(strategy_name).strip()
    evaluator = ALLOWLISTED_EVALUATORS.get(normalized_name)

    if evaluator is None:
        raise UnsupportedStrategyEvaluatorError(
            "strategy has no qualified evaluator: "
            f"{normalized_name or '<empty>'}"
        )

    if normalized_name in MULTI_SYMBOL_EVALUATORS_V1:
        return evaluator(
            str(primary_symbol or "").strip().upper(),
            universe_bars if isinstance(universe_bars, dict) else {},
        )

    return evaluator(bars)

def healthcheck() -> dict[str, object]:
    return {
        "component":
            "reference_strategy_evaluator_registry",

        "healthy":
            True,

        "allowlisted_count":
            len(
                ALLOWLISTED_EVALUATORS
            ),

        "allowlisted_names":
            tuple(
                ALLOWLISTED_EVALUATORS
            ),

        "dynamic_imports":
            False,

        "catalog_formula_execution":
            False,

        "execution_enabled":
            False,
    }


# Qualified fourth batch: globally capable, still user-enable controlled.
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **ALLOWLISTED_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V4,
    }
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    BULK_OFFLINE_EVALUATORS_V5,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **ALLOWLISTED_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V5,
    }
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v6 import (
    BULK_OFFLINE_EVALUATORS_V6,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **ALLOWLISTED_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V6,
    }
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v7 import (
    BULK_OFFLINE_EVALUATORS_V7,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **ALLOWLISTED_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V7,
    }
)


from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v8 import (
    BULK_OFFLINE_EVALUATORS_V8,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {
        **ALLOWLISTED_EVALUATORS,
        **BULK_OFFLINE_EVALUATORS_V8,
    }
)


from backend.app.stacks.strategy.evaluators.multi_symbol_family_v1 import (
    MULTI_SYMBOL_EVALUATORS_V1,
    MULTI_SYMBOL_STRATEGY_NAMES,
)

ALLOWLISTED_EVALUATORS = MappingProxyType(
    {**ALLOWLISTED_EVALUATORS, **MULTI_SYMBOL_EVALUATORS_V1}
)
