from __future__ import annotations

import math

import pytest

from backend.app.stacks.risk import drawdown_guard


@pytest.mark.asyncio
async def test_database_failure_blocks_execution(monkeypatch):
    async def unavailable(*, user_id):
        raise ConnectionError("database unavailable")

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        unavailable,
    )

    result = await drawdown_guard.healthcheck(
        10000.0,
        user_id="owner-1",
    )
    assert result["status"] == "blocked"
    assert result["reason"] == "risk_monitor_unavailable"


@pytest.mark.asyncio
@pytest.mark.parametrize("balance", [
    -1.0,
    math.nan,
    math.inf,
    -math.inf,
])
async def test_invalid_balance_blocks(monkeypatch, balance):
    async def read(*, user_id):
        raise AssertionError("should not query")

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        read,
    )

    result = await drawdown_guard.healthcheck(
        balance,
        user_id="owner-1",
    )
    assert result["status"] == "blocked"


@pytest.mark.asyncio
async def test_invalid_history_blocks(monkeypatch):
    async def read(*, user_id):
        return float("nan")

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        read,
    )

    result = await drawdown_guard.healthcheck(
        10000.0,
        user_id="owner-1",
    )
    assert result["status"] == "blocked"


@pytest.mark.asyncio
async def test_missing_history_preserves_existing_contract(monkeypatch):
    async def read(*, user_id):
        return None

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        read,
    )

    result = await drawdown_guard.healthcheck(
        100000.0,
        user_id="owner-1",
    )
    assert result["status"] == "ok"
    assert result["drawdown_limit_enforced"] is False


@pytest.mark.asyncio
async def test_cash_ratio_is_not_presented_as_loss_guard(monkeypatch):
    async def read(*, user_id):
        return 15000.0

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        read,
    )

    result = await drawdown_guard.healthcheck(
        1485.03,
        user_id="owner-1",
    )
    assert result["status"] == "ok"
    assert result["drawdown_basis"] == "cash_only_diagnostic"
    assert result["drawdown_limit_enforced"] is False


@pytest.mark.asyncio
async def test_missing_owner_blocks_without_query(monkeypatch):
    async def read(*, user_id):
        raise AssertionError("should not query")

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        read,
    )

    result = await drawdown_guard.healthcheck(
        100000.0,
        user_id=" ",
    )
    assert result["status"] == "blocked"
