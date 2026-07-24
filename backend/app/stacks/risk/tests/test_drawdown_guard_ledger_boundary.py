from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.risk import drawdown_guard


ROOT = Path(".").resolve()

LEDGER_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "journal_ledger"
    / "ledger.py"
)

RISK_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "risk"
    / "drawdown_guard.py"
)


def _imports(
    path: Path,
) -> set[str]:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(
                    alias.name
                )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(
                    node.module
                )

    return modules


def _calls(
    path: Path,
) -> set[str]:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    calls = set()

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        expression = node.func
        parts = []

        while isinstance(
            expression,
            ast.Attribute,
        ):
            parts.append(
                expression.attr
            )

            expression = expression.value

        if isinstance(
            expression,
            ast.Name,
        ):
            parts.append(
                expression.id
            )

        if parts:
            calls.add(
                ".".join(
                    reversed(parts)
                )
            )

    return calls


def test_risk_owns_no_persistence_import() -> None:
    imports = _imports(
        RISK_FILE
    )

    assert (
        "backend.app.stacks.journal_ledger.ledger"
    ) in imports

    for module in imports:
        lowered = module.lower()

        assert "sqlalchemy" not in lowered
        assert "db_runtime" not in lowered


def test_risk_imports_no_ledger_internals() -> None:
    source = RISK_FILE.read_text(
        encoding="utf-8"
    )

    assert "async_session" not in source
    assert "OrderHistory" not in source
    assert "session.execute" not in source


def test_risk_calls_only_read_facade() -> None:
    calls = {
        call.split(".")[-1]
        for call in _calls(
            RISK_FILE
        )
    }

    assert (
        "read_max_allocated_capital"
        in calls
    )

    assert not calls & {
        "execute",
        "flush",
        "commit",
        "rollback",
        "add",
        "delete",
        "save_log",
    }


@pytest.mark.asyncio
async def test_healthcheck_preserves_none_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_read(
        *,
        user_id: str,
    ) -> None:
        assert user_id == "risk-owner-1"
        return None

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        fake_read,
    )

    result = await drawdown_guard.healthcheck(
        100.0,
        user_id="risk-owner-1",
    )

    assert result is not NotImplemented


@pytest.mark.asyncio
async def test_healthcheck_uses_scalar_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def fake_read(
        *,
        user_id: str,
    ) -> float:
        nonlocal calls

        assert user_id == "risk-owner-1"

        calls += 1
        return 200000.0

    monkeypatch.setattr(
        drawdown_guard,
        "read_max_allocated_capital",
        fake_read,
    )

    result = await drawdown_guard.healthcheck(
        100.0,
        user_id="risk-owner-1",
    )

    expected_drawdown = (
        200000.0 - 100.0
    ) / 200000.0

    assert calls == 1
    assert result["status"] == "ok"
    assert result["simulation_mode"] is True
    assert result["trailing_drawdown"] == pytest.approx(
        expected_drawdown
    )


def test_ledger_owns_read_query() -> None:
    source = LEDGER_FILE.read_text(
        encoding="utf-8"
    )

    assert (
        "async def read_max_allocated_capital"
        in source
    )

    assert "async_session()" in source
    assert "OrderHistory.allocated_capital" in source
    assert "session.execute" in source


def test_read_facade_exposes_no_session_or_model() -> None:
    tree = ast.parse(
        LEDGER_FILE.read_text(
            encoding="utf-8"
        ),
        filename=str(LEDGER_FILE),
    )

    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name
        == "read_max_allocated_capital"
    ]

    assert len(matches) == 1

    function = matches[0]

    assert (
        ast.unparse(
            function.returns
        )
        == "float | None"
    )
