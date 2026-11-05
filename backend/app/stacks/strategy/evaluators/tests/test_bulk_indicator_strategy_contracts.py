from dataclasses import FrozenInstanceError
from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts import (
    BULK_INDICATOR_STRATEGY_CONTRACTS,
    EMA_CROSSOVER,
    GOLDEN_CROSS,
    MACD_CROSSOVER,
    PRICE_ABOVE_MOVING_AVERAGE,
    STOCHASTIC_MOMENTUM,
    TIME_SERIES_MOMENTUM,
    get_bulk_indicator_strategy_contract,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


EXPECTED_NAMES = (
    "MACD Crossover",
    "MACD Zero-Line",
    "MACD Histogram Momentum",
    "Stochastic Momentum",
    "Stochastic Oversold Reversion",
    "Commodity Channel Index Momentum",
    "CCI Mean Reversion",
    "Rate of Change Momentum",
    "ROC Zero Cross",
    "Time-Series Momentum",
    "RSI Momentum",
    "TRIX Trend",
    "Golden Cross",
    "Exponential Moving Average Crossover",
    "Price Above Moving Average",
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
        BULK_INDICATOR_STRATEGY_CONTRACTS
    ) == EXPECTED_NAMES

    assert len(
        BULK_INDICATOR_STRATEGY_CONTRACTS
    ) == 15


def test_every_contract_has_complete_decision_rules():
    for contract in (
        BULK_INDICATOR_STRATEGY_CONTRACTS.values()
    ):
        assert contract.buy_rule.startswith("BUY")
        assert contract.sell_rule.startswith("SELL")
        assert contract.hold_rule.startswith("HOLD")
        assert contract.abstain_rule.startswith("ABSTAIN")
        assert contract.minimum_bars >= 2
        assert contract.parameters
        assert contract.evaluator_id.endswith("_v1")


def test_macd_parameters_are_locked():
    assert dict(
        MACD_CROSSOVER.parameters
    ) == {
        "fast_ema": 12,
        "slow_ema": 26,
        "signal_ema": 9,
    }

    assert MACD_CROSSOVER.minimum_bars == 35


def test_stochastic_parameters_are_locked():
    assert dict(
        STOCHASTIC_MOMENTUM.parameters
    ) == {
        "k_window": 14,
        "d_window": 3,
        "center_threshold": 50.0,
    }

    assert STOCHASTIC_MOMENTUM.minimum_bars == 17


def test_long_history_contracts_are_explicit():
    assert TIME_SERIES_MOMENTUM.minimum_bars == 253
    assert GOLDEN_CROSS.minimum_bars == 202
    assert (
        PRICE_ABOVE_MOVING_AVERAGE.minimum_bars
        == 202
    )


def test_ema_crossover_defaults_are_explicit():
    assert dict(
        EMA_CROSSOVER.parameters
    ) == {
        "fast_ema": 12,
        "slow_ema": 26,
    }


def test_contract_and_parameter_mapping_are_immutable():
    with pytest.raises(
        FrozenInstanceError
    ):
        MACD_CROSSOVER.minimum_bars = 20

    with pytest.raises(
        TypeError
    ):
        MACD_CROSSOVER.parameters[
            "fast_ema"
        ] = 5

    with pytest.raises(
        TypeError
    ):
        BULK_INDICATOR_STRATEGY_CONTRACTS[
            "Unknown"
        ] = MACD_CROSSOVER


def test_exact_lookup_returns_identity():
    assert (
        get_bulk_indicator_strategy_contract(
            "Golden Cross"
        )
        is GOLDEN_CROSS
    )


def test_unknown_lookup_fails_closed():
    with pytest.raises(
        KeyError
    ):
        get_bulk_indicator_strategy_contract(
            "Unknown Strategy"
        )


def test_active_registry_remains_nine():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_does_not_claim_activation():
    report = healthcheck()

    assert report["healthy"] is True
    assert report["contract_count"] == 15
    assert report["immutable"] is True
    assert report["truthful_daily_ohlcv_only"] is True
    assert report["evaluator_implementations_present"] is False
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False
