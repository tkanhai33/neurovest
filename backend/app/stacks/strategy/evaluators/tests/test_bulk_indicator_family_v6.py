from copy import deepcopy

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v6 import (
    BULK_OFFLINE_EVALUATORS_V6,
    SIXTH_FIFTEEN_OHLCV_NAMES,
    healthcheck,
)


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.16,
            "high": 101.0 + index * 0.16,
            "low": 99.0 + index * 0.16,
            "close": 100.3 + index * 0.16,
            "volume": 1000.0 + index * 13.0,
        }
        for index in range(count)
    ]


def test_exact_sixth_fifteen_identity_order():
    assert tuple(BULK_OFFLINE_EVALUATORS_V6) == SIXTH_FIFTEEN_OHLCV_NAMES
    assert len(BULK_OFFLINE_EVALUATORS_V6) == 15


def test_all_sixth_fifteen_are_canonical_and_non_executable():
    supplied = bars()
    original = deepcopy(supplied)

    for name, evaluator in BULK_OFFLINE_EVALUATORS_V6.items():
        output = evaluator(supplied)
        assert output["strategy_name"] == name
        assert output["decision"] in {"BUY", "SELL", "HOLD", "ABSTAIN"}
        assert output["signal"] == output["decision"]
        assert 0.0 <= output["confidence"] <= 1.0
        assert output["execution_enabled"] is False

    assert supplied == original


def test_short_history_abstains():
    for evaluator in BULK_OFFLINE_EVALUATORS_V6.values():
        assert evaluator(bars(20))["decision"] == "ABSTAIN"


def test_healthcheck_remains_offline_only():
    assert healthcheck()["strategy_count"] == 15
    assert healthcheck()["offline_only"] is True
    assert healthcheck()["execution_enabled"] is False
