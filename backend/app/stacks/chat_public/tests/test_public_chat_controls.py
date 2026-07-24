from __future__ import annotations

import ast
import asyncio
import inspect
from pathlib import Path

import pytest
from fastapi import HTTPException

from backend.app.stacks.chat_public.public_controls import (
    AnonymousSlidingWindowLimiter,
    enforce_public_chat_controls,
    enforce_public_chat_safety,
    validate_public_chat_text,
)


ROOT = Path(".").resolve()

ROUTE_FILE = (
    ROOT
    / 'backend/app/stacks/chat_public/chat_api.py'
)

ROUTE_FUNCTION = 'chat_endpoint'


def test_public_chat_contract_accepts_valid_text() -> None:
    validate_public_chat_text(
        ["Explain portfolio diversification."]
    )


def test_public_chat_contract_rejects_empty_text() -> None:
    with pytest.raises(
        Exception,
        match="cannot be empty",
    ):
        validate_public_chat_text(
            ["   "]
        )


def test_public_chat_contract_rejects_oversized_text() -> None:
    with pytest.raises(
        Exception,
        match="maximum",
    ):
        validate_public_chat_text(
            ["12345"],
            max_text_length=4,
        )


def test_public_chat_safety_denies_restricted_action() -> None:
    with pytest.raises(
        Exception,
        match="restricted",
    ):
        enforce_public_chat_safety(
            ["Please execute a trade for me."]
        )


def test_public_chat_safety_allows_general_discussion() -> None:
    enforce_public_chat_safety(
        [
            "Explain how a trade order works "
            "without performing one."
        ]
    )


@pytest.mark.asyncio
async def test_public_chat_timeout_maps_to_504() -> None:
    async def slow_handler(
        message: str,
    ) -> dict[str, str]:
        await asyncio.sleep(
            0.05
        )

        return {
            "message": message,
        }

    wrapped = enforce_public_chat_controls(
        slow_handler,
        timeout_seconds=0.001,
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            "hello"
        )

    assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_public_chat_dependency_failure_maps_to_503() -> None:
    async def unavailable_handler(
        message: str,
    ) -> None:
        raise RuntimeError(
            "dependency unavailable"
        )

    wrapped = enforce_public_chat_controls(
        unavailable_handler,
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            "hello"
        )

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_public_chat_rate_limit_maps_to_429() -> None:
    async def handler(
        message: str,
    ) -> str:
        return message

    limiter = AnonymousSlidingWindowLimiter(
        limit=1,
        window_seconds=60.0,
    )

    wrapped = enforce_public_chat_controls(
        handler,
        limiter=limiter,
    )

    assert await wrapped(
        "first message"
    ) == "first message"

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            "second message"
        )

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_public_chat_safety_denial_maps_to_403() -> None:
    async def handler(
        message: str,
    ) -> str:
        return message

    wrapped = enforce_public_chat_controls(
        handler,
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            "Enable live trading."
        )

    assert exc_info.value.status_code == 403


def test_route_is_decorated_with_public_controls() -> None:
    source = ROUTE_FILE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(
            ROUTE_FILE
        ),
    )

    matches = [
        node
        for node in ast.walk(
            tree
        )
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == ROUTE_FUNCTION
    ]

    assert len(matches) == 1

    decorators = [
        ast.unparse(
            decorator
        )
        for decorator
        in matches[0].decorator_list
    ]

    assert any(
        decorator.split(
            "(",
            1,
        )[0].split(
            "."
        )[-1]
        == "enforce_public_chat_controls"
        for decorator in decorators
    )


def test_public_control_wrapper_preserves_signature() -> None:
    async def original(
        message: str,
        optional: int = 1,
    ) -> str:
        return message * optional

    wrapped = enforce_public_chat_controls(
        original,
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    assert inspect.signature(
        wrapped
    ) == inspect.signature(
        original
    )



@pytest.mark.asyncio
async def test_payload_boundary_ignores_injected_dependencies() -> None:
    class Payload:
        def model_dump(self) -> dict[str, str]:
            return {
                "message": "hello",
            }

    class LargeDependency:
        def __init__(self) -> None:
            self.internal_state = "x" * 12000

    async def handler(
        payload: Payload,
        dependency: LargeDependency,
    ) -> str:
        return payload.model_dump()["message"]

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    result = await wrapped(
        Payload(),
        LargeDependency(),
    )

    assert result == "hello"


@pytest.mark.asyncio
async def test_payload_boundary_rejects_oversized_payload() -> None:
    class Payload:
        def __init__(
            self,
            message: str,
        ) -> None:
            self.message = message

        def model_dump(self) -> dict[str, str]:
            return {
                "message": self.message,
            }

    async def handler(
        payload: Payload,
        dependency: object,
    ) -> str:
        return payload.message

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="payload",
        max_text_length=8000,
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            Payload("x" * 8001),
            object(),
        )

    assert exc_info.value.status_code == 422
    assert "maximum" in str(
        exc_info.value.detail
    ).lower()


@pytest.mark.asyncio
async def test_payload_boundary_rejects_empty_payload() -> None:
    class Payload:
        def model_dump(self) -> dict[str, str]:
            return {
                "message": "   ",
            }

    async def handler(
        payload: Payload,
    ) -> str:
        return "unexpected"

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            Payload(),
        )

    assert exc_info.value.status_code == 422
    assert "empty" in str(
        exc_info.value.detail
    ).lower()


@pytest.mark.asyncio
async def test_payload_boundary_safety_uses_only_payload() -> None:
    class Payload:
        def model_dump(self) -> dict[str, str]:
            return {
                "message": (
                    "Explain portfolio diversification."
                ),
            }

    class Dependency:
        def __init__(self) -> None:
            self.internal_text = (
                "Enable live trading and execute a trade."
            )

    async def handler(
        payload: Payload,
        dependency: Dependency,
    ) -> str:
        return payload.model_dump()["message"]

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    result = await wrapped(
        Payload(),
        Dependency(),
    )

    assert result == (
        "Explain portfolio diversification."
    )


@pytest.mark.asyncio
async def test_payload_boundary_still_rejects_restricted_payload() -> None:
    class Payload:
        def model_dump(self) -> dict[str, str]:
            return {
                "message": "Enable live trading.",
            }

    async def handler(
        payload: Payload,
    ) -> str:
        return "unexpected"

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            Payload(),
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_payload_argument_fails_closed() -> None:
    async def handler(
        payload: str,
    ) -> str:
        return payload

    wrapped = enforce_public_chat_controls(
        handler,
        payload_argument="missing_payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        await wrapped(
            "hello",
        )

    assert exc_info.value.status_code == 422
    assert "could not be resolved" in str(
        exc_info.value.detail
    ).lower()


def test_configured_payload_wrapper_preserves_signature() -> None:
    async def original(
        payload: str,
        request: object,
    ) -> str:
        return payload

    wrapped = enforce_public_chat_controls(
        original,
        payload_argument="payload",
        limiter=AnonymousSlidingWindowLimiter(
            limit=10,
            window_seconds=60.0,
        ),
    )

    assert inspect.signature(
        wrapped
    ) == inspect.signature(
        original
    )


def test_chat_route_configures_payload_argument() -> None:
    source = ROUTE_FILE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(
            ROUTE_FILE
        ),
    )

    matches = [
        node
        for node in ast.walk(
            tree
        )
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == ROUTE_FUNCTION
    ]

    assert len(matches) == 1

    decorators = matches[0].decorator_list

    control_calls = [
        decorator
        for decorator in decorators
        if isinstance(
            decorator,
            ast.Call,
        )
        and isinstance(
            decorator.func,
            ast.Name,
        )
        and decorator.func.id
        == "enforce_public_chat_controls"
    ]

    assert len(control_calls) == 1

    keyword_values = {
        keyword.arg: ast.literal_eval(
            keyword.value
        )
        for keyword in control_calls[0].keywords
        if keyword.arg is not None
    }

    assert keyword_values[
        "payload_argument"
    ] == "payload"
