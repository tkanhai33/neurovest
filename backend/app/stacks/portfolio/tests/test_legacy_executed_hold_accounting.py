from datetime import datetime
from types import SimpleNamespace

import pytest

from backend.app.stacks.portfolio.accounting import (
    _is_verified_legacy_executed_hold,
)


def record(**changes):
    values = {
        "id": 5,
        "status": "executed",
        "signal": "hold",
        "symbol": "AAPL",
        "timestamp": datetime(2026, 7, 4, 12, 0),
        "allocated_capital": 7829.615756249999,
        "slippage_price": 308.15,
        "commission_paid": 1.0,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_verified_historical_hold_is_exempt():
    assert _is_verified_legacy_executed_hold(record())
    assert _is_verified_legacy_executed_hold(
        record(
            id=36,
            symbol="TSLA",
            timestamp=datetime(2026, 7, 5, 7, 3),
            allocated_capital=7824.96575625,
        )
    )


@pytest.mark.parametrize("changes", [
    {"id": 4},
    {"id": 37},
    {"id": None},
    {"signal": "buy"},
    {"signal": "unknown"},
    {"status": "pending"},
    {"symbol": "UNVERIFIED"},
    {"timestamp": datetime(2026, 7, 6)},
    {"allocated_capital": 100000},
    {"allocated_capital": float("nan")},
    {"slippage_price": 0},
    {"commission_paid": 0},
    {"commission_paid": 2},
])
def test_unverified_records_are_not_exempt(changes):
    assert not _is_verified_legacy_executed_hold(record(**changes))


def test_missing_metadata_fails_closed():
    assert not _is_verified_legacy_executed_hold(
        SimpleNamespace(id=5, signal="hold", status="executed")
    )
