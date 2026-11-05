from __future__ import annotations

from copy import deepcopy

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    BULK_OFFLINE_EVALUATORS_V5,
    FIFTH_FIFTEEN_OHLCV_NAMES,
    healthcheck,
)


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.12,
            "high": 101.0 + index * 0.12,
            "low": 99.0 + index * 0.12,
            "close": 100.2 + index * 0.12,
            "volume": 1000.0 + index * 11.0,
        }
        for index in range(count)
    ]


def test_exact_fifth_fifteen_identity_order():
    assert tuple(BULK_OFFLINE_EVALUATORS_V5) == FIFTH_FIFTEEN_OHLCV_NAMES
    assert len(BULK_OFFLINE_EVALUATORS_V5) == 15


def test_all_fifth_fifteen_return_canonical_non_executable_results():
    supplied = bars()
    original = deepcopy(supplied)

    for name, evaluator in BULK_OFFLINE_EVALUATORS_V5.items():
        output = evaluator(supplied)

        assert output["strategy_name"] == name
        assert output["decision"] in {"BUY", "SELL", "HOLD", "ABSTAIN"}
        assert output["signal"] == output["decision"]
        assert output["status"] in {"ok", "abstain"}
        assert 0.0 <= output["confidence"] <= 1.0
        assert output["execution_enabled"] is False

    assert supplied == original


def test_short_history_abstains_fail_closed():
    for evaluator in BULK_OFFLINE_EVALUATORS_V5.values():
        output = evaluator(bars(20))
        assert output["decision"] == "ABSTAIN"
        assert output["confidence"] == 0.0


def test_healthcheck_retains_offline_boundary():
    assert healthcheck() == {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
