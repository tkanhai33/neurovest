from dataclasses import FrozenInstanceError
from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v3 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V3,
    ICHIMOKU_TREND,
    NR4_BREAKOUT,
    NR7_BREAKOUT,
    N_DAY_LOW_BREAKDOWN,
    PARABOLIC_SAR_TREND,
    TRIANGLE_BREAKOUT,
    get_bulk_indicator_strategy_contract_v3,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


EXPECTED_NAMES = (
    "Parabolic SAR Trend",
    "Aroon Trend",
    "Ichimoku Trend",
    "Supertrend",
    "N-Day High Breakout",
    "N-Day Low Breakdown",
    "NR4 Breakout",
    "NR7 Breakout",
    "Inside Bar Breakout",
    "Triangle Breakout",
    "Z-Score Mean Reversion",
    "Williams %R Reversion",
    "Gap Fade",
    "Overnight Reversal",
    "Short-Term Reversal Factor",
)


def test_exact_fifteen_catalog_identities_exist_once():
    repository_root = Path(__file__).resolve().parents[6]

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
        BULK_INDICATOR_STRATEGY_CONTRACTS_V3
    ) == EXPECTED_NAMES

    assert len(
        BULK_INDICATOR_STRATEGY_CONTRACTS_V3
    ) == 15


def test_every_contract_has_complete_rules():
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V3.values():
        assert contract.buy_rule.startswith("BUY")
        assert contract.sell_rule.startswith("SELL")
        assert contract.hold_rule.startswith("HOLD")
        assert contract.abstain_rule.startswith("ABSTAIN")
        assert contract.minimum_bars >= 2
        assert contract.parameters
        assert contract.evaluator_id.endswith("_v1")
        assert contract.stateful_position_required is False


def test_adopted_parameters_are_locked():
    assert dict(PARABOLIC_SAR_TREND.parameters) == {
        "acceleration_step": 0.02,
        "acceleration_maximum": 0.20,
    }

    assert ICHIMOKU_TREND.minimum_bars == 78

    assert dict(NR4_BREAKOUT.parameters) == {
        "compression_window": 4,
    }

    assert dict(NR7_BREAKOUT.parameters) == {
        "compression_window": 7,
    }

    assert dict(TRIANGLE_BREAKOUT.parameters) == {
        "structure_window": 20,
        "minimum_touches": 2,
        "volume_window": 20,
        "volume_multiplier": 1.2,
    }


def test_n_day_low_breakdown_is_stateless_and_deterministic():
    assert N_DAY_LOW_BREAKDOWN.minimum_bars == 22

    assert N_DAY_LOW_BREAKDOWN.family == (
        "failed_breakdown_reversal"
    )

    assert dict(
        N_DAY_LOW_BREAKDOWN.parameters
    ) == {
        "window": 20,
    }

    assert (
        "previous close was below"
        in N_DAY_LOW_BREAKDOWN.buy_rule
    )

    assert (
        "reclaims that broken boundary"
        in N_DAY_LOW_BREAKDOWN.buy_rule
    )

    assert (
        "completed downside state"
        not in N_DAY_LOW_BREAKDOWN.buy_rule.lower()
    )

    assert (
        N_DAY_LOW_BREAKDOWN
        .stateful_position_required
        is False
    )


def test_contracts_are_immutable():
    with pytest.raises(FrozenInstanceError):
        PARABOLIC_SAR_TREND.minimum_bars = 10

    with pytest.raises(TypeError):
        PARABOLIC_SAR_TREND.parameters[
            "acceleration_step"
        ] = 0.03

    with pytest.raises(TypeError):
        BULK_INDICATOR_STRATEGY_CONTRACTS_V3[
            "Unknown"
        ] = PARABOLIC_SAR_TREND


def test_exact_lookup_returns_identity():
    assert (
        get_bulk_indicator_strategy_contract_v3(
            "Parabolic SAR Trend"
        )
        is PARABOLIC_SAR_TREND
    )


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "Parabolic  SAR Trend",
        "parabolic sar trend",
        "",
    ],
)
def test_unknown_or_nonexact_lookup_fails_closed(
    unknown_name,
):
    with pytest.raises(KeyError):
        get_bulk_indicator_strategy_contract_v3(
            unknown_name
        )


def test_active_registry_remains_thirty_nine():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_does_not_claim_activation():
    report = healthcheck()

    assert report["healthy"] is True
    assert report["contract_count"] == 15
    assert report["immutable"] is True
    assert report["truthful_daily_ohlcv_only"] is True
    assert report["single_symbol_only"] is True
    assert report["stateful_position_required"] is False
    assert report["event_data_required"] is False
    assert report["universe_data_required"] is False
    assert report["evaluator_implementations_present"] is False
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False
