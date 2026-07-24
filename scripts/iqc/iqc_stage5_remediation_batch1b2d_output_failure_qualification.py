#!/usr/bin/env python3

from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2d"
)

CONTRACT_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "wolfden_ai"
    / "local_model_contract.py"
)

AGENT_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "wolfden_ai"
    / "agent_router.py"
)

ADAPTER_FILE = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "chat_public"
    / "ollama_chat_client.py"
)

FULL_LOG = (
    OUTPUT_DIR
    / "full_backend_tests_latest.log"
)

IMPORT_AUDIT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2d_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2d_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2d_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2d_freeze_latest.json"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@dataclass(frozen=True)
class ProbeResult:
    name: str
    passed: bool
    classification: str
    observed: str
    required: str


def rendered_call(
    node: ast.Call,
) -> str:
    expression = node.func
    parts: list[str] = []

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
        return ".".join(
            reversed(parts)
        )

    try:
        return ast.unparse(
            node.func
        )

    except Exception:
        return "<unresolved>"


contract_source = CONTRACT_FILE.read_text(
    encoding="utf-8"
)

agent_source = AGENT_FILE.read_text(
    encoding="utf-8"
)

adapter_source = ADAPTER_FILE.read_text(
    encoding="utf-8"
)

contract_tree = ast.parse(
    contract_source,
    filename=str(CONTRACT_FILE),
)

agent_tree = ast.parse(
    agent_source,
    filename=str(AGENT_FILE),
)

adapter_tree = ast.parse(
    adapter_source,
    filename=str(ADAPTER_FILE),
)

contract_functions = {
    node.name: node
    for node in contract_tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}

contract_classes = {
    node.name: node
    for node in contract_tree.body
    if isinstance(
        node,
        ast.ClassDef,
    )
}

assert (
    "invoke_approved_local_model"
    in contract_functions
)

assert (
    "WolfdenLocalModelResponse"
    in contract_classes
)

invoke_function = contract_functions[
    "invoke_approved_local_model"
]

response_class = contract_classes[
    "WolfdenLocalModelResponse"
]

invoke_calls = sorted(
    {
        rendered_call(
            node
        )
        for node in ast.walk(
            invoke_function
        )
        if isinstance(
            node,
            ast.Call,
        )
    }
)

invoke_raise_types = sorted(
    {
        (
            rendered_call(
                node.exc
            )
            if isinstance(
                node.exc,
                ast.Call,
            )
            else ast.unparse(
                node.exc
            )
        )
        for node in ast.walk(
            invoke_function
        )
        if isinstance(
            node,
            ast.Raise,
        )
        and node.exc is not None
    }
)

invoke_try_nodes = [
    node
    for node in ast.walk(
        invoke_function
    )
    if isinstance(
        node,
        ast.Try,
    )
]

internal_timeout_calls = sorted(
    call
    for call in invoke_calls
    if call in {
        "asyncio.wait_for",
        "asyncio.timeout",
        "wait_for",
    }
)

parser_functions = sorted(
    name
    for name in contract_functions
    if any(
        marker in name.lower()
        for marker in (
            "parse",
            "validate_output",
            "normalize_output",
            "decode",
        )
    )
)

response_fields = []

for node in response_class.body:
    if not isinstance(
        node,
        ast.AnnAssign,
    ):
        continue

    if not isinstance(
        node.target,
        ast.Name,
    ):
        continue

    response_fields.append(
        node.target.id
    )

failure_status_fields = sorted(
    field
    for field in response_fields
    if any(
        marker in field.lower()
        for marker in (
            "accepted",
            "valid",
            "failure",
            "error",
            "status",
            "timed_out",
        )
    )
)

length_bound_literals = sorted(
    {
        node.value
        for node in ast.walk(
            invoke_function
        )
        if isinstance(
            node,
            ast.Constant,
        )
        and isinstance(
            node.value,
            int,
        )
        and 64 <= node.value <= 100000
    }
)

strip_calls = [
    rendered_call(
        node
    )
    for node in ast.walk(
        invoke_function
    )
    if isinstance(
        node,
        ast.Call,
    )
    and rendered_call(
        node
    ).endswith(
        ".strip"
    )
]

json_imported = any(
    (
        isinstance(
            node,
            ast.Import,
        )
        and any(
            alias.name == "json"
            for alias in node.names
        )
    )
    or (
        isinstance(
            node,
            ast.ImportFrom,
        )
        and node.module == "json"
    )
    for node in contract_tree.body
)

json_parse_calls = sorted(
    call
    for call in invoke_calls
    if call in {
        "json.loads",
        "loads",
    }
)

agent_functions = {
    node.name: node
    for node in agent_tree.body
    if isinstance(
        node,
        ast.AsyncFunctionDef,
    )
}

wrapper = agent_functions[
    "monitor_and_process_signals"
]

wrapper_try_nodes = [
    node
    for node in ast.walk(
        wrapper
    )
    if isinstance(
        node,
        ast.Try,
    )
]

wrapper_await_calls = sorted(
    rendered_call(
        node.value
    )
    for node in ast.walk(
        wrapper
    )
    if isinstance(
        node,
        ast.Await,
    )
    and isinstance(
        node.value,
        ast.Call,
    )
)

adapter_functions = {
    node.name: node
    for node in adapter_tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}

assert "ask_ollama" in adapter_functions

from backend.app.stacks.wolfden_ai import (
    agent_router,
)

from backend.app.stacks.wolfden_ai import (
    local_model_contract,
)

from backend.app.stacks.wolfden_ai.local_model_contract import (
    WolfdenLocalModelRequest,
    WolfdenLocalModelResponse,
    invoke_approved_local_model,
)


def request() -> WolfdenLocalModelRequest:
    return WolfdenLocalModelRequest(
        message="test",
        intent="wolfden_signal_advisory",
        symbol="AAPL",
        context={},
    )


async def probe_adapter_value(
    value: Any,
) -> tuple[str, Any]:
    original = (
        local_model_contract.asyncio.to_thread
    )

    async def fake_to_thread(
        function,
        *args,
    ):
        return value

    local_model_contract.asyncio.to_thread = (
        fake_to_thread
    )

    try:
        result = await invoke_approved_local_model(
            request()
        )

        return (
            "returned",
            result,
        )

    except Exception as error:
        return (
            "raised",
            {
                "type": type(
                    error
                ).__name__,
                "message": str(
                    error
                ),
            },
        )

    finally:
        local_model_contract.asyncio.to_thread = (
            original
        )


async def probe_adapter_exception() -> tuple[str, Any]:
    original = (
        local_model_contract.asyncio.to_thread
    )

    async def fake_to_thread(
        function,
        *args,
    ):
        raise ConnectionError(
            "local model unavailable"
        )

    local_model_contract.asyncio.to_thread = (
        fake_to_thread
    )

    try:
        result = await invoke_approved_local_model(
            request()
        )

        return (
            "returned",
            result,
        )

    except Exception as error:
        return (
            "raised",
            {
                "type": type(
                    error
                ).__name__,
                "message": str(
                    error
                ),
            },
        )

    finally:
        local_model_contract.asyncio.to_thread = (
            original
        )


async def probe_wrapper_failure() -> dict[str, Any]:
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
        }

    async def failing_model(
        request,
    ):
        calls["model"] += 1

        raise TimeoutError(
            "model timeout"
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
                local_model_enabled=True,
                local_model_invoke=failing_model,
            )
        )

        return {
            "outcome": "returned",
            "result": result,
            "calls": calls,
        }

    except Exception as error:
        return {
            "outcome": "raised",
            "error_type": type(
                error
            ).__name__,
            "error_message": str(
                error
            ),
            "calls": calls,
        }

    finally:
        agent_router._monitor_and_process_signals_core = (
            original_core
        )


async def run_probes() -> dict[str, Any]:
    plain = await probe_adapter_value(
        "advisory text"
    )

    empty = await probe_adapter_value(
        ""
    )

    whitespace = await probe_adapter_value(
        "   \n\t "
    )

    non_string = await probe_adapter_value(
        {
            "text": "advisory",
        }
    )

    malformed_json = await probe_adapter_value(
        '{"advisory":'
    )

    dangerous_text = await probe_adapter_value(
        (
            "execute trade, connect broker, "
            "enable live trading"
        )
    )

    oversized = await probe_adapter_value(
        "x" * 20000
    )

    adapter_exception = (
        await probe_adapter_exception()
    )

    wrapper_failure = (
        await probe_wrapper_failure()
    )

    return {
        "plain": plain,
        "empty": empty,
        "whitespace": whitespace,
        "non_string": non_string,
        "malformed_json": malformed_json,
        "dangerous_text": dangerous_text,
        "oversized": oversized,
        "adapter_exception": adapter_exception,
        "wrapper_failure": wrapper_failure,
    }


runtime = asyncio.run(
    run_probes()
)


def response_to_dict(
    result: tuple[str, Any],
) -> dict[str, Any]:
    outcome, value = result

    if (
        outcome == "returned"
        and isinstance(
            value,
            WolfdenLocalModelResponse,
        )
    ):
        return {
            "outcome": outcome,
            "response": asdict(
                value
            ),
        }

    return {
        "outcome": outcome,
        "value": value,
    }


runtime_serialized = {
    name: (
        response_to_dict(
            value
        )
        if isinstance(
            value,
            tuple,
        )
        else value
    )
    for name, value in runtime.items()
}

plain_response = runtime_serialized[
    "plain"
]

empty_response = runtime_serialized[
    "empty"
]

whitespace_response = runtime_serialized[
    "whitespace"
]

non_string_response = runtime_serialized[
    "non_string"
]

malformed_json_response = runtime_serialized[
    "malformed_json"
]

dangerous_response = runtime_serialized[
    "dangerous_text"
]

oversized_response = runtime_serialized[
    "oversized"
]

adapter_exception_response = runtime_serialized[
    "adapter_exception"
]

wrapper_failure = runtime_serialized[
    "wrapper_failure"
]

probes: list[ProbeResult] = []

probes.append(
    ProbeResult(
        name="immutable_non_executable_response",
        passed=(
            plain_response[
                "outcome"
            ] == "returned"
            and plain_response[
                "response"
            ][
                "executable"
            ] is False
            and plain_response[
                "response"
            ][
                "mutation_requested"
            ] is False
            and plain_response[
                "response"
            ][
                "broker_access_requested"
            ] is False
        ),
        classification=(
            "PRESENT"
        ),
        observed=repr(
            plain_response
        ),
        required=(
            "Successful responses remain immutable "
            "and non-executable."
        ),
    )
)

probes.append(
    ProbeResult(
        name="explicit_output_parser",
        passed=bool(
            parser_functions
            or json_parse_calls
        ),
        classification=(
            "PRESENT"
            if (
                parser_functions
                or json_parse_calls
            )
            else "MISSING"
        ),
        observed=(
            "parser_functions="
            f"{parser_functions}, "
            "json_parse_calls="
            f"{json_parse_calls}"
        ),
        required=(
            "Model output must pass through an "
            "explicit parser or validator."
        ),
    )
)

probes.append(
    ProbeResult(
        name="empty_output_rejected",
        passed=(
            empty_response[
                "outcome"
            ] != "returned"
        ),
        classification=(
            "PRESENT"
            if empty_response[
                "outcome"
            ] != "returned"
            else "MISSING"
        ),
        observed=repr(
            empty_response
        ),
        required=(
            "Empty model output must not be "
            "accepted as a valid advisory."
        ),
    )
)

probes.append(
    ProbeResult(
        name="whitespace_output_rejected",
        passed=(
            whitespace_response[
                "outcome"
            ] != "returned"
        ),
        classification=(
            "PRESENT"
            if whitespace_response[
                "outcome"
            ] != "returned"
            else "MISSING"
        ),
        observed=repr(
            whitespace_response
        ),
        required=(
            "Whitespace-only model output must "
            "not be accepted."
        ),
    )
)

probes.append(
    ProbeResult(
        name="non_string_output_fail_closed",
        passed=(
            non_string_response[
                "outcome"
            ] == "returned"
            and bool(
                failure_status_fields
            )
        ),
        classification=(
            "PRESENT"
            if (
                non_string_response[
                    "outcome"
                ] == "returned"
                and failure_status_fields
            )
            else (
                "EXCEPTION_ONLY"
                if non_string_response[
                    "outcome"
                ] == "raised"
                else "MISSING"
            )
        ),
        observed=repr(
            non_string_response
        ),
        required=(
            "Non-string output must become an "
            "immutable rejected result instead of "
            "leaking a raw exception."
        ),
    )
)

probes.append(
    ProbeResult(
        name="malformed_structured_output_rejected",
        passed=(
            malformed_json_response[
                "outcome"
            ] != "returned"
        ),
        classification=(
            "PRESENT"
            if malformed_json_response[
                "outcome"
            ] != "returned"
            else "MISSING"
        ),
        observed=repr(
            malformed_json_response
        ),
        required=(
            "Malformed structured output must be "
            "rejected or mapped to a fail-closed result."
        ),
    )
)

probes.append(
    ProbeResult(
        name="bounded_output_length",
        passed=bool(
            length_bound_literals
        )
        and oversized_response[
            "outcome"
        ] != "returned",
        classification=(
            "PRESENT"
            if (
                length_bound_literals
                and oversized_response[
                    "outcome"
                ] != "returned"
            )
            else "MISSING"
        ),
        observed=(
            "length_bounds="
            f"{length_bound_literals}, "
            "runtime="
            f"{oversized_response}"
        ),
        required=(
            "Output length must be bounded before "
            "the advisory is accepted."
        ),
    )
)

probes.append(
    ProbeResult(
        name="internal_invocation_timeout",
        passed=bool(
            internal_timeout_calls
        ),
        classification=(
            "PRESENT"
            if internal_timeout_calls
            else "MISSING"
        ),
        observed=(
            "timeout_calls="
            f"{internal_timeout_calls}"
        ),
        required=(
            "The approved model invocation must "
            "own a bounded internal timeout."
        ),
    )
)

probes.append(
    ProbeResult(
        name="adapter_exception_mapped",
        passed=(
            adapter_exception_response[
                "outcome"
            ] == "returned"
            and bool(
                failure_status_fields
            )
        ),
        classification=(
            "PRESENT"
            if (
                adapter_exception_response[
                    "outcome"
                ] == "returned"
                and failure_status_fields
            )
            else (
                "EXCEPTION_PROPAGATES"
                if adapter_exception_response[
                    "outcome"
                ] == "raised"
                else "MISSING"
            )
        ),
        observed=repr(
            adapter_exception_response
        ),
        required=(
            "Adapter failures must be mapped to an "
            "immutable fail-closed result."
        ),
    )
)

probes.append(
    ProbeResult(
        name="failure_status_contract",
        passed=bool(
            failure_status_fields
        ),
        classification=(
            "PRESENT"
            if failure_status_fields
            else "MISSING"
        ),
        observed=(
            "response_fields="
            f"{response_fields}"
        ),
        required=(
            "The immutable response must explicitly "
            "represent acceptance or failure."
        ),
    )
)

probes.append(
    ProbeResult(
        name="dangerous_text_cannot_unlock_capability",
        passed=(
            dangerous_response[
                "outcome"
            ] == "returned"
            and dangerous_response[
                "response"
            ][
                "executable"
            ] is False
            and dangerous_response[
                "response"
            ][
                "mutation_requested"
            ] is False
            and dangerous_response[
                "response"
            ][
                "broker_access_requested"
            ] is False
        ),
        classification="PRESENT",
        observed=repr(
            dangerous_response
        ),
        required=(
            "Dangerous model text cannot change "
            "execution, mutation, or broker flags."
        ),
    )
)

probes.append(
    ProbeResult(
        name="wrapper_model_failure_preserves_core",
        passed=(
            wrapper_failure[
                "outcome"
            ] == "returned"
            and wrapper_failure[
                "calls"
            ][
                "core"
            ] == 1
        ),
        classification=(
            "PRESENT"
            if (
                wrapper_failure[
                    "outcome"
                ] == "returned"
                and wrapper_failure[
                    "calls"
                ][
                    "core"
                ] == 1
            )
            else (
                "MODEL_FAILURE_BLOCKS_CORE"
                if wrapper_failure[
                    "calls"
                ][
                    "core"
                ] == 0
                else "MISSING"
            )
        ),
        observed=repr(
            wrapper_failure
        ),
        required=(
            "An advisory-model failure must not "
            "replace or prevent the protected "
            "existing Wolfden core path."
        ),
    )
)

probes.append(
    ProbeResult(
        name="wrapper_failure_guard",
        passed=bool(
            wrapper_try_nodes
        ),
        classification=(
            "PRESENT"
            if wrapper_try_nodes
            else "MISSING"
        ),
        observed=(
            "wrapper_try_nodes="
            f"{len(wrapper_try_nodes)}"
        ),
        required=(
            "The opt-in wrapper must explicitly "
            "guard advisory-model failures."
        ),
    )
)

missing_gates = [
    probe.name
    for probe in probes
    if not probe.passed
]

present_gates = [
    probe.name
    for probe in probes
    if probe.passed
]

if missing_gates:
    disposition = (
        "CONFIRMED_LOCAL_MODEL_FAILURE_"
        "CONTROL_REMEDIATION_REQUIRED"
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2D1 — "
        "Implement and Qualify the Confirmed Missing "
        "Wolfden Output, Timeout, and Fail-Closed Controls"
    )

else:
    disposition = (
        "LOCAL_MODEL_FAILURE_CONTROLS_COMPLETE"
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2E — "
        "Wolfden Local-Model End-to-End Qualification "
        "and Baseline Freeze"
    )

authorized_targets = sorted(
    {
        (
            "backend/app/stacks/wolfden_ai/"
            "local_model_contract.py"
        ),
        (
            "backend/app/stacks/wolfden_ai/"
            "agent_router.py"
        ),
        (
            "backend/app/stacks/wolfden_ai/tests/"
            "test_local_model_binding.py"
        ),
    }
)

excluded_targets = sorted(
    {
        (
            "backend/app/stacks/chat_public/"
            "ollama_chat_client.py"
        ),
        (
            "backend/app/stacks/strategy/"
            "llm_strategy_engine.py"
        ),
        (
            "backend/app/stacks/wolfden_ai/"
            "portfolio_output_result_facade.py"
        ),
    }
)

audit = json.loads(
    IMPORT_AUDIT.read_text(
        encoding="utf-8"
    )
)

summary = audit[
    "summary"
]

assert summary[
    "active_internal_unresolved"
] == 0

assert summary[
    "tooling_or_relative_unresolved"
] == 0

assert summary[
    "syntax_errors"
] == 0

assert summary[
    "active_cycle_components"
] == 0

assert summary[
    "self_cycles"
] == 0

test_text = FULL_LOG.read_text(
    encoding="utf-8",
    errors="replace",
)

passed_matches = re.findall(
    r"(\d+)\s+passed",
    test_text,
)

failed_matches = re.findall(
    r"(\d+)\s+failed",
    test_text,
)

tests_passed = (
    int(
        passed_matches[-1]
    )
    if passed_matches
    else 0
)

tests_failed = (
    int(
        failed_matches[-1]
    )
    if failed_matches
    else 0
)

assert tests_passed >= 189
assert tests_failed == 0

source_manifest = []

for path in sorted(
    (
        ROOT
        / "backend"
        / "app"
    ).rglob(
        "*.py"
    )
):
    if "__pycache__" in path.parts:
        continue

    data = path.read_bytes()

    source_manifest.append(
        {
            "path": path.relative_to(
                ROOT
            ).as_posix(),
            "sha256": hashlib.sha256(
                data
            ).hexdigest(),
            "size_bytes": len(data),
        }
    )

evidence = {
    "status": "completed",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "mode": "read_only",
    "static": {
        "invoke_calls": invoke_calls,
        "invoke_raise_types": (
            invoke_raise_types
        ),
        "invoke_try_node_count": len(
            invoke_try_nodes
        ),
        "internal_timeout_calls": (
            internal_timeout_calls
        ),
        "parser_functions": (
            parser_functions
        ),
        "json_imported": (
            json_imported
        ),
        "json_parse_calls": (
            json_parse_calls
        ),
        "response_fields": (
            response_fields
        ),
        "failure_status_fields": (
            failure_status_fields
        ),
        "length_bound_literals": (
            length_bound_literals
        ),
        "strip_calls": (
            strip_calls
        ),
        "wrapper_try_node_count": len(
            wrapper_try_nodes
        ),
        "wrapper_await_calls": (
            wrapper_await_calls
        ),
    },
    "runtime": runtime_serialized,
    "probes": [
        asdict(
            probe
        )
        for probe in probes
    ],
    "present_gates": (
        present_gates
    ),
    "missing_gates": (
        missing_gates
    ),
    "source_manifest": (
        source_manifest
    ),
}

report = {
    "campaign": (
        "NeuroVest Integrated "
        "Qualification Campaign"
    ),
    "batch": (
        "IQC-STAGE5-REM-001B2D"
    ),
    "batch_name": (
        "Qualify Wolfden Local-Model Output Parsing, "
        "Malformed-Output Handling, Timeout, "
        "and Fail-Closed Behavior"
    ),
    "status": "completed",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "mode": "read_only",
    "disposition": disposition,
    "qualification": {
        "gate_count": len(
            probes
        ),
        "present_gate_count": len(
            present_gates
        ),
        "missing_gate_count": len(
            missing_gates
        ),
        "present_gates": (
            present_gates
        ),
        "missing_gates": (
            missing_gates
        ),
        "whole_backend_tests_passed": (
            tests_passed
        ),
        "whole_backend_tests_failed": (
            tests_failed
        ),
        "active_internal_unresolved": 0,
        "tooling_or_relative_unresolved": 0,
        "syntax_errors": 0,
        "active_dependency_cycles": 0,
        "self_cycles": 0,
    },
    "authorized_source_targets": (
        authorized_targets
    ),
    "explicitly_excluded_targets": (
        excluded_targets
    ),
    "source_modified": False,
    "database_modified": False,
    "auth_implemented": False,
    "snaptrade_connected": False,
    "broker_execution_enabled": False,
    "live_trading_enabled": False,
    "public_deployment_authorized": False,
    "next_step": next_step,
}

freeze = {
    "status": "frozen",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "batch": (
        "IQC-STAGE5-REM-001B2D"
    ),
    "disposition": disposition,
    "confirmed_missing_gates": (
        missing_gates
    ),
    "confirmed_present_gates": (
        present_gates
    ),
    "authorized_source_targets": (
        authorized_targets
    ),
    "explicitly_excluded_targets": (
        excluded_targets
    ),
    "source_modified": False,
    "database_modified": False,
    "broker_execution_enabled": False,
    "live_trading_enabled": False,
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

REPORT_JSON.write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

FREEZE_JSON.write_text(
    json.dumps(
        freeze,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

text_lines = [
    "=" * 108,
    "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
    (
        "IQC STAGE 5 REMEDIATION BATCH 1B2D — "
        "QUALIFY WOLFDEN LOCAL-MODEL OUTPUT PARSING, "
        "MALFORMED-OUTPUT HANDLING, TIMEOUT, "
        "AND FAIL-CLOSED BEHAVIOR"
    ),
    "=" * 108,
    "",
    "STATUS",
    "COMPLETE AND VERIFIED",
    "",
    "MODE",
    "READ ONLY",
    "",
    "DISPOSITION",
    disposition,
    "",
    "CONTROL QUALIFICATION",
    (
        "Controls inspected:             "
        f"{len(probes)}"
    ),
    (
        "Controls present:               "
        f"{len(present_gates)}"
    ),
    (
        "Controls missing:               "
        f"{len(missing_gates)}"
    ),
    "",
    "PRESENT CONTROLS",
]

if present_gates:
    text_lines.extend(
        f"- {name}"
        for name in present_gates
    )

else:
    text_lines.append(
        "- None"
    )

text_lines.extend(
    [
        "",
        "CONFIRMED MISSING CONTROLS",
    ]
)

if missing_gates:
    text_lines.extend(
        f"- {name}"
        for name in missing_gates
    )

else:
    text_lines.append(
        "- None"
    )

text_lines.extend(
    [
        "",
        "RUNTIME OBSERVATIONS",
        (
            "Empty output:                 "
            + empty_response[
                "outcome"
            ].upper()
        ),
        (
            "Whitespace output:            "
            + whitespace_response[
                "outcome"
            ].upper()
        ),
        (
            "Non-string output:            "
            + non_string_response[
                "outcome"
            ].upper()
        ),
        (
            "Malformed JSON text:          "
            + malformed_json_response[
                "outcome"
            ].upper()
        ),
        (
            "Oversized output:             "
            + oversized_response[
                "outcome"
            ].upper()
        ),
        (
            "Adapter exception:            "
            + adapter_exception_response[
                "outcome"
            ].upper()
        ),
        (
            "Wrapper model failure:        "
            + wrapper_failure[
                "outcome"
            ].upper()
        ),
        (
            "Core called after failure:    "
            + (
                "YES"
                if wrapper_failure[
                    "calls"
                ][
                    "core"
                ] == 1
                else "NO"
            )
        ),
        "",
        "QUALIFICATION BASELINE",
        (
            "Whole-backend tests passed:   "
            f"{tests_passed}"
        ),
        (
            "Whole-backend tests failed:   "
            f"{tests_failed}"
        ),
        "Active unresolved imports:       0",
        "Dependency cycles:               0",
        "Syntax errors:                   0",
        "",
        "SAFETY",
        "- Source modified: NO",
        "- Database modified: NO",
        "- Auth implemented: NO",
        "- SnapTrade connected: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "- Public deployment authorized: NO",
        "",
        "NEXT",
        next_step,
        "",
        "=" * 108,
    ]
)

rendered = (
    "\n".join(
        text_lines
    )
    + "\n"
)

REPORT_TEXT.write_text(
    rendered,
    encoding="utf-8",
)

print(rendered)

print("DETAILED CONTROL RESULTS")

for probe in probes:
    print()
    print(
        f"- {probe.name}: "
        f"{probe.classification}"
    )

    print(
        f"  Observed: {probe.observed}"
    )

    print(
        f"  Required: {probe.required}"
    )

print()
print("PASS: Batch 1B2D evidence written")
print(REPORT_JSON)
print(EVIDENCE_JSON)
print(FREEZE_JSON)
