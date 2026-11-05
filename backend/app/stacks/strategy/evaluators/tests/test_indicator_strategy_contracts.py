from dataclasses import FrozenInstanceError
from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.indicator_strategy_contracts import (
    BOLLINGER_BREAKOUT,
    BOLLINGER_MEAN_REVERSION,
    BOLLINGER_MINIMUM_BARS,
    BOLLINGER_MULTIPLIER,
    BOLLINGER_WINDOW,
    INDICATOR_STRATEGY_CONTRACTS,
    RSI_MINIMUM_BARS,
    RSI_NEUTRAL,
    RSI_OVERBOUGHT,
    RSI_OVERBOUGHT_MEAN_REVERSION,
    RSI_OVERSOLD,
    RSI_OVERSOLD_MEAN_REVERSION,
    RSI_WINDOW,
    get_indicator_strategy_contract,
    healthcheck,
)


EXPECTED_NAMES = (
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
)


def test_exact_catalog_identities_exist_once():
    repository_root = (
        Path(
            __file__
        )
        .resolve()
        .parents[6]
    )

    catalog_path = (
        repository_root
        /
        "backend/app/stacks/strategy/reference_catalog/catalog.json"
    )

    payload = json.loads(
        catalog_path.read_text(
            encoding="utf-8",
        )
    )

    records = payload[
        "strategies"
    ]

    for name in EXPECTED_NAMES:
        matches = [
            row
            for row in records
            if row.get(
                "strategy_name"
            ) == name
        ]

        assert len(
            matches
        ) == 1


def test_contract_registry_contains_exact_four_names():
    assert tuple(
        INDICATOR_STRATEGY_CONTRACTS
    ) == EXPECTED_NAMES


def test_bollinger_parameters_are_explicit():
    assert BOLLINGER_WINDOW == 20
    assert BOLLINGER_MULTIPLIER == 2.0
    assert BOLLINGER_MINIMUM_BARS == 21

    for contract in (
        BOLLINGER_BREAKOUT,
        BOLLINGER_MEAN_REVERSION,
    ):
        assert contract.window == 20
        assert contract.multiplier == 2.0
        assert contract.minimum_bars == 21
        assert contract.transition_only is True


def test_rsi_parameters_are_explicit():
    assert RSI_WINDOW == 14
    assert RSI_OVERBOUGHT == 70.0
    assert RSI_OVERSOLD == 30.0
    assert RSI_NEUTRAL == 50.0
    assert RSI_MINIMUM_BARS == 16


def test_overbought_contract_is_sell_side_only():
    contract = (
        RSI_OVERBOUGHT_MEAN_REVERSION
    )

    assert (
        contract.overbought_threshold
        ==
        70.0
    )

    assert contract.neutral_threshold == 50.0
    assert contract.minimum_bars == 16
    assert "SELL only" in contract.sell_rule
    assert "No BUY entry" in contract.buy_rule


def test_oversold_contract_is_buy_side_only():
    contract = (
        RSI_OVERSOLD_MEAN_REVERSION
    )

    assert (
        contract.oversold_threshold
        ==
        30.0
    )

    assert contract.neutral_threshold == 50.0
    assert contract.minimum_bars == 16
    assert "BUY only" in contract.buy_rule
    assert "No SELL entry" in contract.sell_rule


def test_all_contracts_define_hold_and_abstain():
    for contract in (
        INDICATOR_STRATEGY_CONTRACTS
        .values()
    ):
        assert contract.hold_rule.startswith(
            "HOLD"
        )

        assert contract.abstain_rule.startswith(
            "ABSTAIN"
        )

        assert contract.transition_only is True


def test_contracts_are_immutable():
    with pytest.raises(
        FrozenInstanceError
    ):
        BOLLINGER_BREAKOUT.window = 10


def test_unknown_contract_fails_closed():
    with pytest.raises(
        KeyError
    ):
        get_indicator_strategy_contract(
            "Unknown Strategy"
        )


def test_exact_lookup_returns_identity():
    assert (
        get_indicator_strategy_contract(
            "Bollinger Band Breakout"
        )
        is BOLLINGER_BREAKOUT
    )


def test_healthcheck_does_not_claim_activation():
    result = healthcheck()

    assert result[
        "healthy"
    ] is True

    assert result[
        "contract_count"
    ] == 4

    assert result[
        "immutable"
    ] is True

    assert result[
        "transition_only"
    ] is True

    assert result[
        "evaluator_implementations_present"
    ] is False

    assert result[
        "registry_activated"
    ] is False

    assert result[
        "execution_enabled"
    ] is False
