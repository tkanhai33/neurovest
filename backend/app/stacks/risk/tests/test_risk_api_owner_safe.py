from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.risk import risk_service


ROOT = Path(__file__).resolve().parents[5]
MAIN = ROOT / "backend/app/main.py"


def test_route_requires_principal_and_passes_owner():
    tree = ast.parse(MAIN.read_text())
    matches = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "api_risk_gate"
    ]
    assert len(matches) == 1
    route = ast.unparse(matches[0])
    assert "require_authenticated_principal" in route
    assert "principal.subject" in route
    assert "owner_subject=principal.subject" in route


@pytest.mark.asyncio
async def test_valid_owner_monitor_never_claims_trade_approval(
    monkeypatch,
):
    async def trace(**kwargs):
        return None

    async def valuation(*, user_id):
        assert user_id == "owner-a"
        return {"current_cash_balance": 1485.03}

    async def guard(balance, *, user_id):
        assert balance == 1485.03
        assert user_id == "owner-a"
        return {
            "status": "ok",
            "drawdown_basis": "cash_only_diagnostic",
            "drawdown_limit_enforced": False,
        }

    monkeypatch.setattr(risk_service, "emit_runtime_step", trace)
    monkeypatch.setattr(
        risk_service,
        "calculate_live_portfolio_equity",
        valuation,
    )
    monkeypatch.setattr(
        risk_service, "drawdown_healthcheck", guard
    )

    result = await risk_service.get_risk_gate_for_api(
        "aapl", owner_subject="owner-a"
    )
    assert result["symbol"] == "AAPL"
    assert result["status"] == "ok"
    assert result["allowed"] is False
    assert result["risk_monitor_available"] is True


@pytest.mark.asyncio
async def test_monitor_failure_blocks(monkeypatch):
    async def trace(**kwargs):
        return None

    async def valuation(*, user_id):
        return {"current_cash_balance": 5000.0}

    async def guard(balance, *, user_id):
        return {
            "status": "blocked",
            "reason": "risk_monitor_unavailable",
        }

    monkeypatch.setattr(risk_service, "emit_runtime_step", trace)
    monkeypatch.setattr(
        risk_service, "calculate_live_portfolio_equity",
        valuation,
    )
    monkeypatch.setattr(
        risk_service, "drawdown_healthcheck", guard
    )

    result = await risk_service.get_risk_gate_for_api(
        "AAPL", owner_subject="owner-a"
    )
    assert result["allowed"] is False
    assert result["status"] == "blocked"


@pytest.mark.asyncio
async def test_valuation_exception_fails_closed(monkeypatch):
    async def trace(**kwargs):
        return None

    async def unavailable(*, user_id):
        raise RuntimeError("private database detail")

    monkeypatch.setattr(risk_service, "emit_runtime_step", trace)
    monkeypatch.setattr(
        risk_service,
        "calculate_live_portfolio_equity",
        unavailable,
    )

    result = await risk_service.get_risk_gate_for_api(
        "AAPL", owner_subject="owner-a"
    )
    assert result["allowed"] is False
    assert result["status"] == "error"
    assert "private database detail" not in str(result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "symbol,owner",
    [("", "owner-a"), ("AAPL", ""), ("AAPL", "  ")],
)
async def test_missing_input_fails_closed(symbol, owner):
    result = await risk_service.get_risk_gate_for_api(
        symbol, owner_subject=owner
    )
    assert result["allowed"] is False
    assert result["status"] == "error"
