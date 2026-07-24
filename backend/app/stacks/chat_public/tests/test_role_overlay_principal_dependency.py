from __future__ import annotations

import ast
import inspect
from pathlib import Path

from fastapi.params import Depends as DependsParameter

from backend.app.stacks.chat_public import (
    chat_api,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)


ROOT = Path(__file__).resolve().parents[5]

CHAT_API_PATH = (
    ROOT
    / "backend/app/stacks/chat_public/chat_api.py"
)


def _chat_endpoint():
    matching = [
        route.endpoint
        for route in chat_api.router.routes
        if getattr(route, "path", None)
        == "/api/v1/chat"
    ]

    assert len(matching) == 1

    endpoint = matching[0]

    while hasattr(endpoint, "__wrapped__"):
        endpoint = endpoint.__wrapped__

    return endpoint


def test_chat_endpoint_has_authenticated_principal_dependency() -> None:
    endpoint = _chat_endpoint()
    signature = inspect.signature(endpoint)

    assert "principal" in signature.parameters

    parameter = signature.parameters[
        "principal"
    ]

    assert (
        parameter.annotation
        is AuthenticatedPrincipal
        or str(parameter.annotation)
        in {
            "AuthenticatedPrincipal",
            "'AuthenticatedPrincipal'",
        }
    )

    dependency = parameter.default

    assert isinstance(
        dependency,
        DependsParameter,
    )

    assert (
        dependency.dependency
        is require_authenticated_principal
    )


def test_chat_endpoint_passes_principal_to_runtime() -> None:
    tree = ast.parse(
        CHAT_API_PATH.read_text(
            encoding="utf-8"
        )
    )

    endpoint = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name == "chat_endpoint"
    )

    runtime_calls = [
        node
        for node in ast.walk(endpoint)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "run_chat_turn"
    ]

    assert len(runtime_calls) == 1

    principal_keywords = [
        keyword
        for keyword in runtime_calls[0].keywords
        if keyword.arg == "principal"
    ]

    assert len(principal_keywords) == 1

    value = principal_keywords[0].value

    assert isinstance(value, ast.Name)
    assert value.id == "principal"


def test_chat_endpoint_has_no_undefined_principal_reference() -> None:
    tree = ast.parse(
        CHAT_API_PATH.read_text(
            encoding="utf-8"
        )
    )

    endpoint = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name == "chat_endpoint"
    )

    parameter_names = {
        argument.arg
        for argument in (
            list(endpoint.args.posonlyargs)
            + list(endpoint.args.args)
            + list(endpoint.args.kwonlyargs)
        )
    }

    assert "principal" in parameter_names
