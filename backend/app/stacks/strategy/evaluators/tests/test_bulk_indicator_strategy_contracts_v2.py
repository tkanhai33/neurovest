from dataclasses import FrozenInstanceError
from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v2 import (
    ADX_BREAKOUT,
    ATR_COMPRESSION_EXPANSION,
    BULK_INDICATOR_STRATEGY_CONTRACTS_V2,
    MOVING_AVERAGE_RIBBON,
    STOCHASTIC_PULLBACK_IN_TREND,
    TRIPLE_MOVING_AVERAGE_TREND,
    get_bulk_indicator_strategy_contract_v2,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


EXPECTED_NAMES = (
    "Stochastic Pullback in Trend",
    "High-Low Momentum",
    "Price Acceleration",
    "ADX Breakout",
    "ADX Trend Following",
    "DMI Crossover",
    "Hull Moving Average Trend",
    "Moving Average Ribbon",
    "Envelope Mean Reversion",
    "Moving Average Deviation Reversion",
    "Moving Average Crossover with ATR Filter",
    "Moving Average Slope",
    "Triple Moving Average Trend",
    "ATR Compression Expansion",
    "Money Flow Index Reversion",
)


def test_exact_fifteen_catalog_identities_exist_once():
    repository_root = (
        Path(__file__).resolve().parents[6]
    )

    catalog_path = (
        repository_root
        / "backend/app/stacks/strategy/reference_catalog/catalog.json"
    )

    records = json.loads(
        catalog_path.read_text(
            encoding="utf-8",
        )
    )["strategies"]

    for name in EXPECTED_NAMES:
        assert sum(
            record.get("strategy_name") == name
            for record in records
        ) == 1


def test_mapping_contains_exact_stable_fifteen():
    assert tuple(
        BULK_INDICATOR_STRATEGY_CONTRACTS_V2
    ) == EXPECTED_NAMES

    assert len(
        BULK_INDICATOR_STRATEGY_CONTRACTS_V2
    ) == 15


def test_every_contract_has_complete_rules():
    for contract in (
        BULK_INDICATOR_STRATEGY_CONTRACTS_V2.values()
    ):
        assert contract.buy_rule.startswith("BUY")
        assert contract.sell_rule.startswith("SELL")
        assert contract.hold_rule.startswith("HOLD")
        assert contract.abstain_rule.startswith("ABSTAIN")
        assert contract.minimum_bars >= 2
        assert contract.parameters
        assert contract.evaluator_id.endswith("_v1")
        assert contract.stateful_position_required is False


def test_stochastic_trend_parameters_are_locked():
    assert dict(
        STOCHASTIC_PULLBACK_IN_TREND.parameters
    ) == {
        "k_window": 14,
        "d_window": 3,
        "trend_sma": 200,
        "oversold_threshold": 20.0,
        "overbought_threshold": 80.0,
    }

    assert (
        STOCHASTIC_PULLBACK_IN_TREND.minimum_bars
        == 202
    )


def test_adx_breakout_parameters_are_locked():
    assert dict(
        ADX_BREAKOUT.parameters
    ) == {
        "adx_window": 14,
        "adx_threshold": 25.0,
        "breakout_window": 20,
    }


def test_moving_average_ribbon_is_explicit():
    assert dict(
        MOVING_AVERAGE_RIBBON.parameters
    ) == {
        "ma_1": 10,
        "ma_2": 20,
        "ma_3": 50,
        "ma_4": 100,
        "ma_5": 200,
    }

    assert MOVING_AVERAGE_RIBBON.minimum_bars == 202


def test_triple_moving_average_is_explicit():
    assert dict(
        TRIPLE_MOVING_AVERAGE_TREND.parameters
    ) == {
        "short_sma": 20,
        "medium_sma": 50,
        "long_sma": 200,
    }


def test_atr_compression_parameters_are_explicit():
    assert dict(
        ATR_COMPRESSION_EXPANSION.parameters
    ) == {
        "atr_window": 14,
        "percentile_window": 100,
        "compression_percentile": 20.0,
        "breakout_window": 20,
    }


def test_contracts_and_parameter_mappings_are_immutable():
    with pytest.raises(
        FrozenInstanceError
    ):
        ADX_BREAKOUT.minimum_bars = 10

    with pytest.raises(
        TypeError
    ):
        ADX_BREAKOUT.parameters[
            "adx_window"
        ] = 5

    with pytest.raises(
        TypeError
    ):
        BULK_INDICATOR_STRATEGY_CONTRACTS_V2[
            "Unknown"
        ] = ADX_BREAKOUT


def test_exact_lookup_returns_identity():
    assert (
        get_bulk_indicator_strategy_contract_v2(
            "ADX Breakout"
        )
        is ADX_BREAKOUT
    )


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "ADX  Breakout",
        "adx breakout",
        "",
    ],
)
def test_unknown_or_nonexact_lookup_fails_closed(
    unknown_name,
):
    with pytest.raises(
        KeyError
    ):
        get_bulk_indicator_strategy_contract_v2(
            unknown_name
        )


def test_active_registry_remains_twenty_four():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_does_not_claim_activation():
    report = healthcheck()

    assert report["healthy"] is True
    assert report["contract_count"] == 15
    assert report["immutable"] is True
    assert report["truthful_daily_ohlcv_only"] is True
    assert report["stateful_position_required"] is False
    assert report["position_sizing_enabled"] is False
    assert report["evaluator_implementations_present"] is False
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False
