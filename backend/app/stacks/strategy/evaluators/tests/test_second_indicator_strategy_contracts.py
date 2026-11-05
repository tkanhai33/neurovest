from dataclasses import FrozenInstanceError
from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.second_indicator_strategy_contracts import (
    ATR_BREAKOUT_MINIMUM_BARS,
    ATR_BREAKOUT_MULTIPLIER,
    ATR_VOLATILITY_BREAKOUT,
    ATR_WINDOW,
    DONCHIAN_CHANNEL_BREAKOUT,
    DONCHIAN_MINIMUM_BARS,
    DONCHIAN_WINDOW,
    KELTNER_ATR_WINDOW,
    KELTNER_CHANNEL_BREAKOUT,
    KELTNER_EMA_WINDOW,
    KELTNER_MINIMUM_BARS,
    KELTNER_MULTIPLIER,
    PREVIOUS_CLOSE_ATR_MULTIPLIER,
    PREVIOUS_CLOSE_ATR_WINDOW,
    PREVIOUS_CLOSE_MINIMUM_BARS,
    SECOND_INDICATOR_STRATEGY_CONTRACTS,
    VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
    get_second_indicator_strategy_contract,
    healthcheck,
)


EXPECTED_NAMES = (
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
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
            record
            for record in records
            if record.get(
                "strategy_name"
            ) == name
        ]

        assert len(
            matches
        ) == 1


def test_contract_registry_contains_exact_four_names():
    assert tuple(
        SECOND_INDICATOR_STRATEGY_CONTRACTS
    ) == EXPECTED_NAMES


def test_donchian_parameters_are_explicit():
    assert DONCHIAN_WINDOW == 20
    assert DONCHIAN_MINIMUM_BARS == 22

    contract = DONCHIAN_CHANNEL_BREAKOUT

    assert contract.channel_window == 20
    assert contract.minimum_bars == 22
    assert contract.transition_only is True
    assert "preceding 20 completed bars" in (
        contract.reference_rule
    )


def test_atr_breakout_parameters_are_explicit():
    assert ATR_WINDOW == 14
    assert ATR_BREAKOUT_MULTIPLIER == 2.0
    assert ATR_BREAKOUT_MINIMUM_BARS == 16

    contract = ATR_VOLATILITY_BREAKOUT

    assert contract.atr_window == 14
    assert contract.atr_multiplier == 2.0
    assert contract.minimum_bars == 16
    assert contract.transition_only is True


def test_keltner_parameters_are_explicit():
    assert KELTNER_EMA_WINDOW == 20
    assert KELTNER_ATR_WINDOW == 14
    assert KELTNER_MULTIPLIER == 2.0
    assert KELTNER_MINIMUM_BARS == 21

    contract = KELTNER_CHANNEL_BREAKOUT

    assert contract.ema_window == 20
    assert contract.atr_window == 14
    assert contract.atr_multiplier == 2.0
    assert contract.minimum_bars == 21
    assert contract.transition_only is True


def test_previous_close_parameters_are_explicit():
    assert PREVIOUS_CLOSE_ATR_WINDOW == 14
    assert PREVIOUS_CLOSE_ATR_MULTIPLIER == 1.0
    assert PREVIOUS_CLOSE_MINIMUM_BARS == 15

    contract = (
        VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE
    )

    assert contract.atr_window == 14
    assert contract.atr_multiplier == 1.0
    assert contract.minimum_bars == 15
    assert contract.transition_only is False


def test_previous_close_uses_truthful_daily_range():
    contract = (
        VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE
    )

    assert "Current truthful high and low" in (
        contract.reference_rule
    )

    assert "daily OHLC cannot reveal" in (
        contract.dual_trigger_rule
    )


def test_all_contracts_define_every_decision():
    for contract in (
        SECOND_INDICATOR_STRATEGY_CONTRACTS
        .values()
    ):
        assert contract.buy_rule.startswith(
            "BUY"
        )

        assert contract.sell_rule.startswith(
            "SELL"
        )

        assert contract.hold_rule.startswith(
            "HOLD"
        )

        assert contract.abstain_rule.startswith(
            "ABSTAIN"
        )


def test_all_contracts_fail_closed_on_dual_trigger():
    for contract in (
        SECOND_INDICATOR_STRATEGY_CONTRACTS
        .values()
    ):
        assert contract.dual_trigger_rule
        assert "ABSTAIN" in (
            contract.dual_trigger_rule
        )


def test_contracts_are_immutable():
    with pytest.raises(
        FrozenInstanceError
    ):
        DONCHIAN_CHANNEL_BREAKOUT.channel_window = 10


def test_contract_mapping_is_immutable():
    with pytest.raises(
        TypeError
    ):
        SECOND_INDICATOR_STRATEGY_CONTRACTS[
            "Unknown"
        ] = DONCHIAN_CHANNEL_BREAKOUT


def test_exact_lookup_returns_identity():
    assert (
        get_second_indicator_strategy_contract(
            "Keltner Channel Breakout"
        )
        is KELTNER_CHANNEL_BREAKOUT
    )


def test_unknown_contract_fails_closed():
    with pytest.raises(
        KeyError
    ):
        get_second_indicator_strategy_contract(
            "Unknown Strategy"
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
        "truthful_daily_ohlc_only"
    ] is True

    assert result[
        "dual_trigger_fails_closed"
    ] is True

    assert result[
        "evaluator_implementations_present"
    ] is False

    assert result[
        "registry_activated"
    ] is False

    assert result[
        "owner_integration_present"
    ] is False

    assert result[
        "execution_enabled"
    ] is False
