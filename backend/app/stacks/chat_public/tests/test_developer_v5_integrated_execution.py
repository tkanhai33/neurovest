import asyncio
import re
from pathlib import Path
from types import SimpleNamespace

from backend.app.stacks.chat_public import (
    developer_awareness_integration_v5 as integration,
    developer_model_synthesis_v5 as synthesis,
    developer_ollama_bridge_v5 as bridge,
)
from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    load_verified_index,
)


ROOT = Path(__file__).resolve().parents[5]


def identity(owner="developer", thread_owner="developer"):
    principal = SimpleNamespace(subject=owner)
    thread = SimpleNamespace(
        thread_id="integration-test-thread",
        user_id=thread_owner,
    )
    return principal, thread


def execute(principal, thread, question):
    return asyncio.run(
        integration.maybe_grounded_developer_answer(
            root=ROOT,
            principal=principal,
            thread=thread,
            question=question,
        )
    )


def test_real_candidate_is_fresh():
    index_path = (
        ROOT
        / "runtime/qualification"
        / "neuro_v5_developer_candidate"
        / "evidence_index.json"
    )

    data = load_verified_index(ROOT, index_path)

    assert len(data["sources"]) >= 24
    assert (
        "backend/app/stacks/chat_public/chat_runtime.py"
        in data["sources"]
    )


def test_enabled_developer_receives_grounded_model_answer(
    monkeypatch,
):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )

    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: principal.subject == "developer",
    )
    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: principal.subject == "developer",
    )

    observed = []

    async def fake_model(prompt):
        observed.append(prompt)

        section = prompt.split(
            "ALLOWED SOURCE REFERENCES:\n", 1
        )[1].split(
            "\n\nVERIFIED STRUCTURAL OBSERVATIONS:", 1
        )[0]

        locations = [
            line.strip()
            for line in section.splitlines()
            if re.fullmatch(
                r"[\w./-]+\.py:\d+",
                line.strip(),
            )
        ]

        assert locations

        return (
            "The verified source contains a definition at "
            + locations[0]
            + ". This establishes a source location, "
            "but does not establish that the function "
            "executed during a live request."
        )

    monkeypatch.setattr(
        bridge,
        "make_local_model",
        lambda **kwargs: fake_model,
    )

    principal, thread = identity()

    answer = execute(
        principal,
        thread,
        "Explain our chat runtime",
    )

    assert len(observed) == 1
    assert "does not establish" in answer
    assert "Verified developer source references" not in answer


def test_ordinary_user_never_reaches_model(monkeypatch):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )

    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: False,
    )

    def unexpected(**kwargs):
        raise AssertionError("Model adapter invoked")

    monkeypatch.setattr(
        bridge, "make_local_model", unexpected
    )

    principal, thread = identity(owner="ordinary-user")
    assert execute(
        principal, thread, "Inspect our code"
    ) is None


def test_other_users_thread_never_reaches_model(monkeypatch):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )

    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: True,
    )

    def unexpected(**kwargs):
        raise AssertionError("Model adapter invoked")

    monkeypatch.setattr(
        bridge, "make_local_model", unexpected
    )

    principal, thread = identity(
        thread_owner="different-owner"
    )

    assert execute(
        principal, thread, "Inspect our code"
    ) is None


def test_invalid_model_output_uses_verified_fallback(
    monkeypatch,
):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )

    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: True,
    )
    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: True,
    )

    async def fake_model(prompt):
        return (
            "I ran the tests and deployed the fix at "
            "fabricated.py:999."
        )

    monkeypatch.setattr(
        bridge,
        "make_local_model",
        lambda **kwargs: fake_model,
    )

    principal, thread = identity()

    answer = execute(
        principal,
        thread,
        "Explain our chat runtime",
    )

    assert "Verified developer source references" in answer
    assert "fabricated.py:999" not in answer


def test_disabled_feature_does_not_invoke_model(
    monkeypatch,
):
    monkeypatch.delenv(
        "NEURO_V5_GROUNDED_AWARENESS",
        raising=False,
    )

    def unexpected(**kwargs):
        raise AssertionError("Model adapter invoked")

    monkeypatch.setattr(
        bridge, "make_local_model", unexpected
    )

    principal, thread = identity()

    assert execute(
        principal, thread, "Explain our chat runtime"
    ) is None
