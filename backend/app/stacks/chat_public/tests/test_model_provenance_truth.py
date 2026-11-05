from __future__ import annotations

from pathlib import Path
import ast

from backend.app.stacks.chat_public.ollama_chat_client import (
    resolve_runtime_model,
)


ROOT = Path(__file__).resolve().parents[5]

RUNTIME = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "chat_public"
    / "chat_runtime.py"
)


def test_neuro_reason_model_resolves_to_its_real_local_tag() -> None:
    assert (
        resolve_runtime_model(
            "neuro-reason:latest"
        )
        == "neuro-reason:latest"
    )


def test_neuro_fast_model_resolves_to_its_real_local_tag() -> None:
    assert (
        resolve_runtime_model(
            "neuro-fast-no-think:latest"
        )
        == "neuro-fast-no-think:latest"
    )


def test_outward_chat_response_uses_resolved_model() -> None:
    source = RUNTIME.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(RUNTIME),
    )

    matches = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue

        for key, value in zip(
            node.keys,
            node.values,
        ):
            if not (
                isinstance(key, ast.Constant)
                and key.value == "model"
            ):
                continue

            if not isinstance(value, ast.Call):
                continue

            if not (
                isinstance(value.func, ast.Name)
                and value.func.id
                == "resolve_runtime_model"
            ):
                continue

            matches.append(node.lineno)

    assert len(matches) == 1


def test_missing_model_remains_none_without_inference() -> None:
    assert resolve_runtime_model(None) is None

