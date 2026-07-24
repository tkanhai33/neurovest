from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Awaitable, Callable, Mapping

from backend.app.stacks.chat_public.ollama_chat_client import (
    ask_ollama,
)


LOCAL_MODEL_TIMEOUT_SECONDS = 30.0
MAX_LOCAL_MODEL_OUTPUT_CHARS = 8192

LocalModelInvoker = Callable[
    ["WolfdenLocalModelRequest"],
    Awaitable["WolfdenLocalModelResponse"],
]


@dataclass(frozen=True, slots=True)
class WolfdenLocalModelRequest:
    message: str
    intent: str
    symbol: str | None
    context: Mapping[str, str]
    execution_allowed: bool = False
    mutation_allowed: bool = False
    broker_access_allowed: bool = False


@dataclass(frozen=True, slots=True)
class WolfdenLocalModelResponse:
    text: str
    accepted: bool = True
    status: str = "accepted"
    failure_code: str | None = None
    provider: str = "ollama-local"
    executable: bool = False
    mutation_requested: bool = False
    broker_access_requested: bool = False


def _safe_text(
    value: Any,
) -> str:
    rendered = repr(value)

    if len(rendered) > 500:
        return rendered[:497] + "..."

    return rendered


def build_local_model_request(
    *,
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> WolfdenLocalModelRequest:
    symbol_value = kwargs.get("symbol")

    symbol = (
        str(symbol_value)
        if symbol_value is not None
        else None
    )

    context = MappingProxyType(
        {
            "args": _safe_text(args),
            "kwargs": _safe_text(
                dict(kwargs)
            ),
        }
    )

    message = (
        "Evaluate the supplied Wolfden signal context. "
        "Return advisory text only. Do not request or "
        "claim execution, persistence mutation, broker "
        "access, or live trading."
    )

    return WolfdenLocalModelRequest(
        message=message,
        intent="wolfden_signal_advisory",
        symbol=symbol,
        context=context,
    )


def rejected_local_model_response(
    failure_code: str,
) -> WolfdenLocalModelResponse:
    return WolfdenLocalModelResponse(
        text="",
        accepted=False,
        status="rejected",
        failure_code=failure_code,
    )


def parse_local_model_output(
    value: Any,
) -> WolfdenLocalModelResponse:
    if not isinstance(value, str):
        return rejected_local_model_response(
            "non_string_output"
        )

    normalized = value.strip()

    if not normalized:
        return rejected_local_model_response(
            "empty_output"
        )

    if len(normalized) > MAX_LOCAL_MODEL_OUTPUT_CHARS:
        return rejected_local_model_response(
            "output_too_large"
        )

    if normalized.startswith(
        (
            "{",
            "[",
        )
    ):
        try:
            decoded = json.loads(
                normalized
            )

        except json.JSONDecodeError:
            return rejected_local_model_response(
                "malformed_structured_output"
            )

        if isinstance(decoded, dict):
            advisory = decoded.get(
                "advisory"
            )

            if not isinstance(advisory, str):
                return rejected_local_model_response(
                    "invalid_structured_output"
                )

            normalized = advisory.strip()

            if not normalized:
                return rejected_local_model_response(
                    "empty_output"
                )

            if (
                len(normalized)
                > MAX_LOCAL_MODEL_OUTPUT_CHARS
            ):
                return rejected_local_model_response(
                    "output_too_large"
                )

        elif isinstance(decoded, str):
            normalized = decoded.strip()

            if not normalized:
                return rejected_local_model_response(
                    "empty_output"
                )

        else:
            return rejected_local_model_response(
                "invalid_structured_output"
            )

    return WolfdenLocalModelResponse(
        text=normalized,
    )


async def invoke_approved_local_model(
    request: WolfdenLocalModelRequest,
) -> WolfdenLocalModelResponse:
    if request.execution_allowed:
        return rejected_local_model_response(
            "execution_forbidden"
        )

    if request.mutation_allowed:
        return rejected_local_model_response(
            "mutation_forbidden"
        )

    if request.broker_access_allowed:
        return rejected_local_model_response(
            "broker_access_forbidden"
        )

    try:
        raw_output = await asyncio.wait_for(
            asyncio.to_thread(
                ask_ollama,
                request.message,
                request.intent,
                request.symbol,
            ),
            timeout=LOCAL_MODEL_TIMEOUT_SECONDS,
        )

    except TimeoutError:
        return rejected_local_model_response(
            "timeout"
        )

    except Exception:
        return rejected_local_model_response(
            "adapter_unavailable"
        )

    return parse_local_model_output(
        raw_output
    )
