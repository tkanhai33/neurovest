from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from backend.app.stacks.chat_public.cognitive_model_router import (
    NEURO_CODE_MODEL,
    NEURO_FALLBACK_MODEL,
    NEURO_FAST_MODEL,
    NEURO_REASON_MODEL,
    route_cognitive_request,
)


ROOT = Path(__file__).resolve().parents[5]

FAST_MODELFILE = (
    ROOT
    / "runtime"
    / "cognitive_engine"
    / "model_profiles"
    / "Modelfile.neuro-fast"
)

REASON_MODELFILE = (
    ROOT
    / "runtime"
    / "cognitive_engine"
    / "model_profiles"
    / "Modelfile.neuro-reason"
)


def make_intent(
    *,
    intent_name: str = "general_conversation",
    family: str = "GENERAL",
    subtype: str = "discussion",
    developer_mode: bool = False,
):
    return SimpleNamespace(
        intent=intent_name,
        family=family,
        subtype=subtype,
        developer_mode=developer_mode,
        requires_repo_context=False,
        requires_architecture_context=False,
    )


def test_fast_profile_is_canonical() -> None:
    assert NEURO_FAST_MODEL == "neuro-fast:latest"

    source = FAST_MODELFILE.read_text(
        encoding="utf-8",
    )

    assert "FROM qwen3:8b" in source
    assert "PARAMETER num_ctx 8192" in source
    assert "simulation and paper-trading only" in source
    assert "Never claim to place live broker orders" in source


def test_reason_profile_is_canonical() -> None:
    assert NEURO_REASON_MODEL == "neuro-reason:latest"

    source = REASON_MODELFILE.read_text(
        encoding="utf-8",
    )

    assert "FROM qwen3-coder:latest" in source
    assert "PARAMETER num_ctx 16384" in source
    assert "Never fabricate prices" in source
    assert "Never promise returns" in source


def test_code_and_fallback_profiles_remain_separate() -> None:
    assert NEURO_CODE_MODEL == "qwen3-coder:latest"
    assert NEURO_FALLBACK_MODEL == "llama3.1:latest"


def test_general_request_routes_to_neuro_fast() -> None:
    decision = route_cognitive_request(
        "Hello Neuro",
        intent=make_intent(),
    )

    assert decision.tier == "fast"
    assert decision.model == "neuro-fast:latest"


def test_strategy_request_routes_to_neuro_reason() -> None:
    decision = route_cognitive_request(
        "Create a paper momentum strategy with risk controls.",
        intent=make_intent(
            intent_name="trading_conversation",
            family="STRATEGY",
            subtype="strategy_creation",
        ),
    )

    assert decision.tier == "reason"
    assert decision.model == "neuro-reason:latest"


def test_developer_request_still_routes_to_code_model() -> None:
    decision = route_cognitive_request(
        "Debug this FastAPI endpoint.",
        intent=make_intent(
            family="DEVELOPER",
            developer_mode=True,
        ),
    )

    assert decision.tier == "code"
    assert decision.model == "qwen3-coder:latest"


def test_model_profiles_do_not_grant_execution_authority() -> None:
    combined = (
        FAST_MODELFILE.read_text(
            encoding="utf-8",
        )
        + REASON_MODELFILE.read_text(
            encoding="utf-8",
        )
    ).lower()

    assert "never claim to place live broker orders" in combined
    assert "paper-trading only" in combined
    assert "bypass authentication" in combined


def test_profile_files_are_plain_text_contracts() -> None:
    payload = {
        "fast": FAST_MODELFILE.read_text(
            encoding="utf-8",
        ),
        "reason": REASON_MODELFILE.read_text(
            encoding="utf-8",
        ),
    }

    json.dumps(payload)
