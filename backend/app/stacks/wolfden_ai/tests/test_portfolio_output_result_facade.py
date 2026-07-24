from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.app.stacks.wolfden_ai.portfolio_output_result_facade import (
    WolfdenPortfolioOutputResult,
    build_portfolio_output_result,
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

FACADE_FILE = (
    WOLFDEN_ROOT
    / "portfolio_output_result_facade.py"
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
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                modules.add(alias.name)

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                modules.add(node.module)

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


def test_result_is_immutable() -> None:
    result = build_portfolio_output_result(
        {"symbol": "AAPL"}
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.status = "MUTATED"  # type: ignore[misc]


def test_result_is_non_executable() -> None:
    result = build_portfolio_output_result(
        symbol="AAPL",
        action="BUY",
    )

    assert result.executable is False
    assert result.mutation_applied is False
    assert result.broker_requested is False
    assert result.status == "ADVISORY_ONLY"


def test_result_rejects_executable_state() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be executable",
    ):
        WolfdenPortfolioOutputResult(
            status="INVALID",
            source="wolfden_ai",
            executable=True,
            mutation_applied=False,
            broker_requested=False,
            payload=(),
        )


def test_payload_is_deeply_frozen() -> None:
    original = {
        "symbols": [
            "AAPL",
            "MSFT",
        ],
    }

    result = build_portfolio_output_result(
        original
    )

    original["symbols"].append(
        "TSLA"
    )

    frozen_payload = dict(
        result.payload
    )

    assert frozen_payload[
        "arg_0"
    ] == (
        (
            "symbols",
            (
                "AAPL",
                "MSFT",
            ),
        ),
    )


def test_result_has_serializable_mapping_contract() -> None:
    result = build_portfolio_output_result(
        symbol="AAPL"
    )

    rendered = result.to_dict()

    assert rendered == {
        "status": "ADVISORY_ONLY",
        "source": "wolfden_ai",
        "executable": False,
        "mutation_applied": False,
        "broker_requested": False,
        "payload": {
            "symbol": "AAPL",
        },
    }

    assert dict(result) == rendered


def test_agent_router_uses_wolfden_facade_only() -> None:
    imports = _imports(
        AGENT_FILE
    )

    assert (
        "backend.app.stacks.wolfden_ai."
        "portfolio_output_result_facade"
    ) in imports

    assert (
        "backend.app.stacks.execution.paper_broker"
    ) not in imports


def test_wolfden_owns_no_execution_or_mutation_capability() -> None:
    forbidden_imports = []
    forbidden_calls = []

    forbidden_stacks = {
        "execution",
        "paper_trading",
        "broker_integration",
        "snaptrade",
    }

    forbidden_terminals = {
        "process_portfolio_output",
        "execute",
        "execute_order",
        "execute_trade",
        "place_order",
        "submit_order",
        "commit",
        "rollback",
        "add",
        "flush",
        "append_event",
    }

    for path in sorted(
        WOLFDEN_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        if (
            "tests" in path.parts
            or path.name.startswith(
                "test_"
            )
        ):
            continue

        for module in _imports(path):
            parts = module.split(".")

            if (
                "stacks" in parts
                and any(
                    stack in parts
                    for stack
                    in forbidden_stacks
                )
            ):
                forbidden_imports.append(
                    (
                        path.relative_to(
                            ROOT
                        ).as_posix(),
                        module,
                    )
                )

        for call in _calls(path):
            if (
                call.split(".")[-1]
                in forbidden_terminals
            ):
                forbidden_calls.append(
                    (
                        path.relative_to(
                            ROOT
                        ).as_posix(),
                        call,
                    )
                )

    assert forbidden_imports == []
    assert forbidden_calls == []
