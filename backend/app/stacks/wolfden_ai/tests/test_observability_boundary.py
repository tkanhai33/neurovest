from __future__ import annotations

import ast
import asyncio
import logging
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.app.stacks.wolfden_ai.observability_boundary import (
    WolfdenObservation,
    record_wolfden_observation,
)


ROOT = Path(".").resolve()

WOLFDEN_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "wolfden_ai"
)

AGENT_FILE = (
    WOLFDEN_ROOT
    / "agent_router.py"
)

BOUNDARY_FILE = (
    WOLFDEN_ROOT
    / "observability_boundary.py"
)

LEDGER_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "journal_ledger"
    / "ledger.py"
)

EXECUTION_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "execution"
    / "paper_broker.py"
)


def _tree(
    path: Path,
) -> ast.Module:
    return ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )


def _imports(
    path: Path,
) -> set[str]:
    modules = set()

    for node in ast.walk(
        _tree(path)
    ):
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
    calls = set()

    for node in ast.walk(
        _tree(path)
    ):
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


def test_observation_is_immutable() -> None:
    event = asyncio.run(
        record_wolfden_observation(
            symbol="AAPL"
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        event.source = "changed"  # type: ignore[misc]


def test_observation_is_non_persistent() -> None:
    event = asyncio.run(
        record_wolfden_observation(
            symbol="AAPL"
        )
    )

    assert event.source == "wolfden_ai"
    assert event.persistent is False
    assert event.mutation_requested is False


def test_observation_rejects_persistent_state() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be persistent",
    ):
        WolfdenObservation(
            event_name="invalid",
            source="wolfden_ai",
            persistent=True,
            mutation_requested=False,
            payload=(),
        )


def test_observation_rejects_mutation_request() -> None:
    with pytest.raises(
        ValueError,
        match="cannot request mutation",
    ):
        WolfdenObservation(
            event_name="invalid",
            source="wolfden_ai",
            persistent=False,
            mutation_requested=True,
            payload=(),
        )


def test_payload_is_deeply_frozen() -> None:
    original = {
        "symbols": [
            "AAPL",
            "MSFT",
        ],
    }

    event = asyncio.run(
        record_wolfden_observation(
            original
        )
    )

    original["symbols"].append(
        "TSLA"
    )

    payload = dict(
        event.payload
    )

    assert payload["arg_0"] == (
        (
            "symbols",
            (
                "AAPL",
                "MSFT",
            ),
        ),
    )


def test_standard_logging_is_used(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(
        logging.INFO,
        logger="neurovest.wolfden_ai",
    ):
        event = asyncio.run(
            record_wolfden_observation(
                event_name="signal_checked",
                symbol="AAPL",
            )
        )

    assert event.event_name == "signal_checked"

    assert any(
        record.message
        == "wolfden_observation"
        for record in caplog.records
    )


def test_agent_router_uses_observability_boundary() -> None:
    imports = _imports(
        AGENT_FILE
    )

    calls = _calls(
        AGENT_FILE
    )

    assert (
        "backend.app.stacks.wolfden_ai."
        "observability_boundary"
    ) in imports

    assert (
        "backend.app.stacks.journal_ledger.ledger"
    ) not in imports

    assert (
        "record_wolfden_observation"
        in calls
    )

    assert "save_log" not in calls


def test_boundary_owns_no_persistence_or_execution() -> None:
    imports = _imports(
        BOUNDARY_FILE
    )

    calls = _calls(
        BOUNDARY_FILE
    )

    for module in imports:
        lowered = module.lower()

        assert not any(
            marker in lowered
            for marker in (
                "sqlalchemy",
                "db_runtime",
                "journal_ledger",
                "execution",
                "paper_trading",
                "broker",
                "snaptrade",
                "portfolio",
            )
        )

    forbidden_calls = {
        "save_log",
        "add",
        "append_event",
        "commit",
        "rollback",
        "flush",
        "execute",
        "execute_order",
        "execute_trade",
        "place_order",
        "submit_order",
        "process_portfolio_output",
    }

    assert not {
        call.split(".")[-1]
        for call in calls
    } & forbidden_calls


def test_journal_ledger_and_execution_are_preserved() -> None:
    ledger_source = LEDGER_FILE.read_text(
        encoding="utf-8"
    )

    execution_source = EXECUTION_FILE.read_text(
        encoding="utf-8"
    )

    assert "def save_log(" in ledger_source
    assert "save_log(" in execution_source
