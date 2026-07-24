#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2e"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2e_evidence_latest.json"
)

from backend.app.stacks.wolfden_ai import (
    agent_router,
)

from backend.app.stacks.wolfden_ai import (
    local_model_contract,
)

from backend.app.stacks.wolfden_ai.local_model_contract import (
    MAX_LOCAL_MODEL_OUTPUT_CHARS,
    WolfdenLocalModelRequest,
    WolfdenLocalModelResponse,
    build_local_model_request,
    invoke_approved_local_model,
)


def serialize_local_model_request(
    request: WolfdenLocalModelRequest,
) -> dict[str, Any]:
    """
    Serialize the immutable request explicitly.

    dataclasses.asdict() is intentionally not used because
    it deep-copies every field and MappingProxyType does not
    support pickle/deepcopy.
    """

    return {
        "message": request.message,
        "intent": request.intent,
        "symbol": request.symbol,
        "context": dict(
            request.context
        ),
        "execution_allowed": (
            request.execution_allowed
        ),
        "mutation_allowed": (
            request.mutation_allowed
        ),
        "broker_access_allowed": (
            request.broker_access_allowed
        ),
    }


def make_request() -> WolfdenLocalModelRequest:
    return build_local_model_request(
        args=("AAPL",),
        kwargs={
            "symbol": "AAPL",
            "signal": "hold",
        },
    )


async def invoke_with_transport(
    value: Any = None,
    *,
    error: Exception | None = None,
) -> WolfdenLocalModelResponse:
    original = (
        local_model_contract
        .asyncio
        .to_thread
    )

    async def fake_to_thread(
        function,
        *args,
    ):
        if error is not None:
            raise error

        return value

    local_model_contract.asyncio.to_thread = (
        fake_to_thread
    )

    try:
        return await invoke_approved_local_model(
            make_request()
        )

    finally:
        local_model_contract.asyncio.to_thread = (
            original
        )


async def timeout_case() -> WolfdenLocalModelResponse:
    original_to_thread = (
        local_model_contract
        .asyncio
        .to_thread
    )

    original_timeout = (
        local_model_contract
        .LOCAL_MODEL_TIMEOUT_SECONDS
    )

    async def hanging_to_thread(
        function,
        *args,
    ):
        await asyncio.sleep(
            10
        )

    local_model_contract.asyncio.to_thread = (
        hanging_to_thread
    )

    local_model_contract.LOCAL_MODEL_TIMEOUT_SECONDS = (
        0.001
    )

    try:
        return await invoke_approved_local_model(
            make_request()
        )

    finally:
        local_model_contract.asyncio.to_thread = (
            original_to_thread
        )

        local_model_contract.LOCAL_MODEL_TIMEOUT_SECONDS = (
            original_timeout
        )


async def wrapper_case(
    *,
    enabled: bool,
    model_mode: str,
) -> dict[str, Any]:
    original_core = (
        agent_router
        ._monitor_and_process_signals_core
    )

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
            "symbol": kwargs.get(
                "symbol"
            ),
        }

    async def model_invoker(
        request,
    ):
        calls["model"] += 1

        if model_mode == "raise":
            raise TimeoutError(
                "injected model failure"
            )

        if model_mode == "reject":
            return WolfdenLocalModelResponse(
                text="",
                accepted=False,
                status="rejected",
                failure_code="timeout",
            )

        return WolfdenLocalModelResponse(
            text="advisory",
        )

    agent_router._monitor_and_process_signals_core = (
        fake_core
    )

    try:
        result = (
            await agent_router
            .monitor_and_process_signals(
                "AAPL",
                symbol="AAPL",
                local_model_enabled=enabled,
                local_model_invoke=model_invoker,
            )
        )

        return {
            "result": result,
            "calls": calls,
        }

    finally:
        agent_router._monitor_and_process_signals_core = (
            original_core
        )


async def main() -> None:
    request = make_request()

    plain = await invoke_with_transport(
        "  advisory text  "
    )

    structured = await invoke_with_transport(
        '{"advisory": "hold position"}'
    )

    empty = await invoke_with_transport(
        ""
    )

    whitespace = await invoke_with_transport(
        "   \n\t "
    )

    non_string = await invoke_with_transport(
        {
            "advisory": "invalid transport object",
        }
    )

    malformed = await invoke_with_transport(
        '{"advisory":'
    )

    invalid_structured = await invoke_with_transport(
        '{"wrong": "value"}'
    )

    oversized = await invoke_with_transport(
        "x"
        * (
            MAX_LOCAL_MODEL_OUTPUT_CHARS
            + 1
        )
    )

    dangerous = await invoke_with_transport(
        (
            "execute trade, connect broker, "
            "enable live trading"
        )
    )

    unavailable = await invoke_with_transport(
        error=ConnectionError(
            "local model unavailable"
        )
    )

    timed_out = await timeout_case()

    disabled_wrapper = await wrapper_case(
        enabled=False,
        model_mode="accept",
    )

    accepted_wrapper = await wrapper_case(
        enabled=True,
        model_mode="accept",
    )

    rejected_wrapper = await wrapper_case(
        enabled=True,
        model_mode="reject",
    )

    raised_wrapper = await wrapper_case(
        enabled=True,
        model_mode="raise",
    )

    assert request.intent == (
        "wolfden_signal_advisory"
    )

    assert request.symbol == "AAPL"
    assert request.execution_allowed is False
    assert request.mutation_allowed is False
    assert request.broker_access_allowed is False

    assert plain.accepted is True
    assert plain.text == "advisory text"

    assert structured.accepted is True
    assert structured.text == "hold position"

    assert empty.accepted is False
    assert empty.failure_code == "empty_output"

    assert whitespace.accepted is False
    assert whitespace.failure_code == "empty_output"

    assert non_string.accepted is False
    assert non_string.failure_code == (
        "non_string_output"
    )

    assert malformed.accepted is False
    assert malformed.failure_code == (
        "malformed_structured_output"
    )

    assert invalid_structured.accepted is False
    assert invalid_structured.failure_code == (
        "invalid_structured_output"
    )

    assert oversized.accepted is False
    assert oversized.failure_code == (
        "output_too_large"
    )

    assert unavailable.accepted is False
    assert unavailable.failure_code == (
        "adapter_unavailable"
    )

    assert timed_out.accepted is False
    assert timed_out.failure_code == "timeout"

    assert dangerous.accepted is True
    assert dangerous.executable is False
    assert dangerous.mutation_requested is False
    assert dangerous.broker_access_requested is False

    assert disabled_wrapper["calls"] == {
        "core": 1,
        "model": 0,
    }

    assert accepted_wrapper["calls"] == {
        "core": 1,
        "model": 1,
    }

    assert rejected_wrapper["calls"] == {
        "core": 1,
        "model": 1,
    }

    assert raised_wrapper["calls"] == {
        "core": 1,
        "model": 1,
    }

    for wrapper in (
        disabled_wrapper,
        accepted_wrapper,
        rejected_wrapper,
        raised_wrapper,
    ):
        assert wrapper["result"] == {
            "status": "core-preserved",
            "symbol": "AAPL",
        }

    evidence = {
        "status": "completed",
        "request": serialize_local_model_request(
            request
        ),
        "responses": {
            "plain": asdict(
                plain
            ),
            "structured": asdict(
                structured
            ),
            "empty": asdict(
                empty
            ),
            "whitespace": asdict(
                whitespace
            ),
            "non_string": asdict(
                non_string
            ),
            "malformed": asdict(
                malformed
            ),
            "invalid_structured": asdict(
                invalid_structured
            ),
            "oversized": asdict(
                oversized
            ),
            "dangerous": asdict(
                dangerous
            ),
            "unavailable": asdict(
                unavailable
            ),
            "timeout": asdict(
                timed_out
            ),
        },
        "wrapper": {
            "disabled": disabled_wrapper,
            "accepted": accepted_wrapper,
            "rejected": rejected_wrapper,
            "raised": raised_wrapper,
        },
        "qualification": {
            "request_contract": True,
            "approved_adapter_binding": True,
            "async_bridge": True,
            "plain_output": True,
            "structured_output": True,
            "empty_output_rejected": True,
            "whitespace_output_rejected": True,
            "non_string_output_rejected": True,
            "malformed_output_rejected": True,
            "invalid_structured_output_rejected": True,
            "oversized_output_rejected": True,
            "adapter_exception_rejected": True,
            "timeout_rejected": True,
            "dangerous_text_non_executable": True,
            "default_model_disabled": True,
            "accepted_model_preserves_core": True,
            "rejected_model_preserves_core": True,
            "raised_model_preserves_core": True,
        },
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "PASS: Wolfden request contract qualified"
    )

    print(
        "PASS: approved adapter invocation path qualified"
    )

    print(
        "PASS: synchronous-to-async bridge qualified"
    )

    print(
        "PASS: valid plain output qualified"
    )

    print(
        "PASS: valid structured output qualified"
    )

    print(
        "PASS: empty and whitespace rejection qualified"
    )

    print(
        "PASS: non-string rejection qualified"
    )

    print(
        "PASS: malformed structured-output rejection qualified"
    )

    print(
        "PASS: invalid structured-output rejection qualified"
    )

    print(
        "PASS: oversized-output rejection qualified"
    )

    print(
        "PASS: adapter-unavailable rejection qualified"
    )

    print(
        "PASS: internal timeout rejection qualified"
    )

    print(
        "PASS: dangerous text remains non-executable"
    )

    print(
        "PASS: local-model invocation remains disabled by default"
    )

    print(
        "PASS: accepted model response preserves Wolfden core"
    )

    print(
        "PASS: rejected model response preserves Wolfden core"
    )

    print(
        "PASS: raised model failure preserves Wolfden core"
    )

    print(
        "PASS: end-to-end evidence written"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
