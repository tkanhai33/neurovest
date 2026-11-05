from copy import deepcopy

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v7 import (
    BULK_OFFLINE_EVALUATORS_V7,
    SEVENTH_FIFTEEN_OHLCV_NAMES,
    healthcheck,
)


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.14,
            "high": 101.2 + index * 0.14,
            "low": 99.1 + index * 0.14,
            "close": 100.4 + index * 0.14,
            "volume": 1000.0 + index * 10.0,
        }
        for index in range(count)
    ]


def test_exact_seventh_fifteen_identity_order():
    assert tuple(BULK_OFFLINE_EVALUATORS_V7) == SEVENTH_FIFTEEN_OHLCV_NAMES
    assert len(BULK_OFFLINE_EVALUATORS_V7) == 15


def test_all_seventh_fifteen_are_canonical_and_non_executable():
    supplied = bars()
    original = deepcopy(supplied)

    for name, evaluator in BULK_OFFLINE_EVALUATORS_V7.items():
        output = evaluator(supplied)

        assert output["strategy_name"] == name
        assert output["decision"] in {"BUY", "SELL", "HOLD", "ABSTAIN"}
        assert output["signal"] == output["decision"]
        assert output["status"] in {"ok", "abstain"}
        assert 0.0 <= output["confidence"] <= 1.0
        assert output["execution_enabled"] is False

    assert supplied == original


def test_short_history_abstains_fail_closed():
    for evaluator in BULK_OFFLINE_EVALUATORS_V7.values():
        output = evaluator(bars(20))
        assert output["decision"] == "ABSTAIN"
        assert output["confidence"] == 0.0


def test_healthcheck_remains_offline_only():
    assert healthcheck() == {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
