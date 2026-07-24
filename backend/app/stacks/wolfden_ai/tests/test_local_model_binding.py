from __future__ import annotations

import ast
import asyncio
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.app.stacks.wolfden_ai import agent_router
from backend.app.stacks.wolfden_ai import local_model_contract
from backend.app.stacks.wolfden_ai.local_model_contract import (
    MAX_LOCAL_MODEL_OUTPUT_CHARS,
    WolfdenLocalModelRequest,
    WolfdenLocalModelResponse,
    build_local_model_request,
    invoke_approved_local_model,
    parse_local_model_output,
)


ROOT = Path(".").resolve()

AGENT_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "wolfden_ai"
    / "agent_router.py"
)

CONTRACT_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "wolfden_ai"
    / "local_model_contract.py"
)


def request() -> WolfdenLocalModelRequest:
    return WolfdenLocalModelRequest(
        message="message",
        intent="intent",
        symbol="AAPL",
        context={},
    )


def test_request_contract_is_immutable() -> None:
    value = build_local_model_request(
        args=("AAPL",),
        kwargs={
            "symbol": "AAPL",
        },
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        value.symbol = "MSFT"


def test_response_contract_is_immutable() -> None:
    value = WolfdenLocalModelResponse(
        text="advisory"
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        value.text = "changed"


def test_response_contract_has_failure_status() -> None:
    value = parse_local_model_output(
        ""
    )

    assert value.accepted is False
    assert value.status == "rejected"
    assert value.failure_code == "empty_output"
    assert value.executable is False
    assert value.mutation_requested is False
    assert value.broker_access_requested is False


def test_valid_plain_output_is_normalized() -> None:
    value = parse_local_model_output(
        "  advisory text  "
    )

    assert value.accepted is True
    assert value.status == "accepted"
    assert value.failure_code is None
    assert value.text == "advisory text"


def test_valid_structured_output_is_parsed() -> None:
    value = parse_local_model_output(
        '{"advisory": "hold position"}'
    )

    assert value.accepted is True
    assert value.text == "hold position"


@pytest.mark.parametrize(
    (
        "raw",
        "failure_code",
    ),
    [
        (
            "",
            "empty_output",
        ),
        (
            "   \n\t ",
            "empty_output",
        ),
        (
            {
                "advisory": "hold",
            },
            "non_string_output",
        ),
        (
            '{"advisory":',
            "malformed_structured_output",
        ),
        (
            '{"wrong": "value"}',
            "invalid_structured_output",
        ),
    ],
)
def test_invalid_output_fails_closed(
    raw,
    failure_code: str,
) -> None:
    value = parse_local_model_output(
        raw
    )

    assert value.accepted is False
    assert value.status == "rejected"
    assert value.failure_code == failure_code
    assert value.text == ""
    assert value.executable is False
    assert value.mutation_requested is False
    assert value.broker_access_requested is False


def test_oversized_output_fails_closed() -> None:
    value = parse_local_model_output(
        "x"
        * (
            MAX_LOCAL_MODEL_OUTPUT_CHARS
            + 1
        )
    )

    assert value.accepted is False
    assert value.failure_code == "output_too_large"


def test_dangerous_text_cannot_unlock_capability() -> None:
    value = parse_local_model_output(
        (
            "execute trade, connect broker, "
            "enable live trading"
        )
    )

    assert value.accepted is True
    assert value.executable is False
    assert value.mutation_requested is False
    assert value.broker_access_requested is False


@pytest.mark.asyncio
async def test_approved_adapter_uses_timeout_bridge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    async def fake_to_thread(
        function,
        *args,
    ):
        captured["function"] = function
        captured["args"] = args
        return "local response"

    monkeypatch.setattr(
        local_model_contract.asyncio,
        "to_thread",
        fake_to_thread,
    )

    value = await invoke_approved_local_model(
        request()
    )

    assert captured["function"].__name__ == "ask_ollama"
    assert captured["args"] == (
        "message",
        "intent",
        "AAPL",
    )

    assert value.accepted is True
    assert value.text == "local response"


@pytest.mark.asyncio
async def test_internal_timeout_maps_to_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def hanging_to_thread(
        function,
        *args,
    ):
        await asyncio.sleep(
            10
        )

    monkeypatch.setattr(
        local_model_contract.asyncio,
        "to_thread",
        hanging_to_thread,
    )

    monkeypatch.setattr(
        local_model_contract,
        "LOCAL_MODEL_TIMEOUT_SECONDS",
        0.001,
    )

    value = await invoke_approved_local_model(
        request()
    )

    assert value.accepted is False
    assert value.failure_code == "timeout"


@pytest.mark.asyncio
async def test_adapter_exception_maps_to_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing_to_thread(
        function,
        *args,
    ):
        raise ConnectionError(
            "unavailable"
        )

    monkeypatch.setattr(
        local_model_contract.asyncio,
        "to_thread",
        failing_to_thread,
    )

    value = await invoke_approved_local_model(
        request()
    )

    assert value.accepted is False
    assert value.status == "rejected"
    assert value.failure_code == "adapter_unavailable"


@pytest.mark.asyncio
async def test_non_string_adapter_output_maps_to_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_to_thread(
        function,
        *args,
    ):
        return {
            "text": "invalid transport result",
        }

    monkeypatch.setattr(
        local_model_contract.asyncio,
        "to_thread",
        fake_to_thread,
    )

    value = await invoke_approved_local_model(
        request()
    )

    assert value.accepted is False
    assert value.failure_code == "non_string_output"


@pytest.mark.asyncio
async def test_default_wrapper_preserves_core_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {
        "core": 0,
        "model": 0,
    }

    async def fake_core(
        *args,
        **kwargs,
    ):
        calls["core"] += 1

        return {
            "status": "preserved",
        }

    async def fake_model(
        model_request,
    ):
        calls["model"] += 1

        return WolfdenLocalModelResponse(
            text="unused"
        )

    monkeypatch.setattr(
        agent_router,
        "_monitor_and_process_signals_core",
        fake_core,
    )

    result = await agent_router.monitor_and_process_signals(
        "AAPL",
        local_model_invoke=fake_model,
    )

    assert result == {
        "status": "preserved",
    }

    assert calls == {
        "core": 1,
        "model": 0,
    }


@pytest.mark.asyncio
async def test_model_failure_cannot_block_core(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {
        "core": 0,
        "model": 0,
    }

    async def fake_core(
        *args,
        **kwargs,
    ):
        calls["core"] += 1

        return {
            "status": "core-preserved",
        }

    async def failing_model(
        model_request,
    ):
        calls["model"] += 1

        raise TimeoutError(
            "model timeout"
        )

    monkeypatch.setattr(
        agent_router,
        "_monitor_and_process_signals_core",
        fake_core,
    )

    result = await agent_router.monitor_and_process_signals(
        "AAPL",
        symbol="AAPL",
        local_model_enabled=True,
        local_model_invoke=failing_model,
    )

    assert result == {
        "status": "core-preserved",
    }

    assert calls == {
        "core": 1,
        "model": 1,
    }


@pytest.mark.asyncio
async def test_rejected_response_cannot_block_core(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {
        "core": 0,
        "model": 0,
    }

    async def fake_core(
        *args,
        **kwargs,
    ):
        calls["core"] += 1

        return {
            "status": "core-preserved",
        }

    async def rejecting_model(
        model_request,
    ):
        calls["model"] += 1

        return WolfdenLocalModelResponse(
            text="",
            accepted=False,
            status="rejected",
            failure_code="timeout",
        )

    monkeypatch.setattr(
        agent_router,
        "_monitor_and_process_signals_core",
        fake_core,
    )

    result = await agent_router.monitor_and_process_signals(
        "AAPL",
        local_model_enabled=True,
        local_model_invoke=rejecting_model,
    )

    assert result == {
        "status": "core-preserved",
    }

    assert calls == {
        "core": 1,
        "model": 1,
    }


def test_agent_wrapper_has_failure_guard() -> None:
    tree = ast.parse(
        AGENT_FILE.read_text(
            encoding="utf-8"
        ),
        filename=str(
            AGENT_FILE
        ),
    )

    wrappers = [
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name
        == "monitor_and_process_signals"
    ]

    assert len(wrappers) == 1

    try_nodes = [
        node
        for node in ast.walk(
            wrappers[0]
        )
        if isinstance(
            node,
            ast.Try,
        )
    ]

    assert len(try_nodes) >= 1


def test_contract_owns_timeout_and_parser() -> None:
    tree = ast.parse(
        CONTRACT_FILE.read_text(
            encoding="utf-8"
        ),
        filename=str(
            CONTRACT_FILE
        ),
    )

    function_names = {
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    assert "parse_local_model_output" in function_names
    assert "invoke_approved_local_model" in function_names

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

    assert "asyncio.wait_for" in calls
    assert "asyncio.to_thread" in calls
    assert "json.loads" in calls


def test_contract_owns_no_mutation_capability() -> None:
    source = CONTRACT_FILE.read_text(
        encoding="utf-8"
    ).lower()

    for forbidden_import in (
        "backend.app.stacks.execution",
        "backend.app.stacks.paper_trading",
        "backend.app.stacks.broker_integration",
        "backend.app.stacks.db_runtime",
        "backend.app.stacks.journal_ledger",
        "sqlalchemy",
    ):
        assert forbidden_import not in source
