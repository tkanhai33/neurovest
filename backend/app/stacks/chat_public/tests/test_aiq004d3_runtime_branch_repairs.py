from __future__ import annotations

from unittest.mock import patch

from backend.app.stacks.chat_public.chat_intent_regex import (
    ChatIntent,
)
from backend.app.stacks.chat_public.chat_runtime import (
    handle_chat_message,
)
from backend.app.stacks.chat_public.strategy_proposal_capture import (
    capture_strategy_proposal,
    extract_symbol,
)


def test_software_debugging_reaches_coder_generation() -> None:
    intent = ChatIntent(
        intent="general_conversation",
        family="DEVELOPER",
        subtype="software_debugging",
        confidence=1.0,
        developer_mode=True,
    )

    with (
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "detect_chat_intent",
            return_value=intent,
        ),
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "route_cognitive_request"
        ) as route,
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "ask_ollama",
            return_value="Inspect the traceback and server logs.",
        ) as ask,
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "capture_strategy_proposal",
            return_value=None,
        ),
    ):
        route.return_value.model = "neuro-reason:latest"
        route.return_value.fallback_model = "neuro-fast:latest"
        route.return_value.retrieval_required = False
        route.return_value.deterministic_tool_required = False
        route.return_value.as_dict.return_value = {
            "model": "neuro-reason:latest",
        }

        result = handle_chat_message(
            "Help me debug a FastAPI endpoint returning HTTP 500.",
            developer_evidence_allowed=True,
        )

    ask.assert_called_once()

    assert result["provider"] != "neurovest_local_evidence"
    assert result["model"] == "neuro-reason:latest"
    assert result["cognitive_route"] is not None


def test_explicit_developer_review_remains_deterministic() -> None:
    intent = ChatIntent(
        intent="general_conversation",
        family="DEVELOPER",
        subtype="developer_review",
        confidence=1.0,
        developer_mode=True,
        requires_repo_context=True,
        requires_architecture_context=True,
    )

    with (
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "detect_chat_intent",
            return_value=intent,
        ),
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "build_developer_response",
            return_value="Developer review",
        ) as builder,
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "ask_ollama"
        ) as ask,
        patch(
            "backend.app.stacks.chat_public.chat_runtime."
            "capture_strategy_proposal",
            return_value=None,
        ),
    ):
        result = handle_chat_message(
            "Review NeuroVest architecture.",
            developer_evidence_allowed=True,
        )

    builder.assert_called_once_with(subtype='developer_review', message='Review NeuroVest architecture.')
    ask.assert_not_called()

    assert result["provider"] == "neurovest_local_evidence"
    assert result["model"] is None
    assert result["cognitive_route"] is None


def test_http_is_not_extracted_as_a_symbol() -> None:
    message = (
        "Help me debug a FastAPI endpoint returning HTTP 500."
    )

    assert extract_symbol(message) is None


def test_real_uppercase_ticker_can_still_be_extracted() -> None:
    assert extract_symbol(
        "Explain an RSI strategy for AAPL."
    ) == "RSI"

    assert extract_symbol(
        "Discuss AAPL price behavior."
    ) == "AAPL"


def test_nonfinancial_intent_never_creates_strategy_candidate() -> None:
    result = capture_strategy_proposal(
        "Help me debug an HTTP endpoint.",
        "Check the API logs and retry strategy.",
        intent="general_conversation",
        symbol=None,
        owner_user_id="test-owner",
    )

    assert result is None


def test_strategy_library_identity_route_never_creates_strategy_candidate(
    tmp_path,
) -> None:

    with patch(
        "backend.app.stacks.chat_public.strategy_proposal_capture."
        "OUT_DIR",
        tmp_path,
    ):

        result = capture_strategy_proposal(
            (
                "Which reference strategy is currently enabled in my "
                "Strategy Library? Answer using my enabled Strategy "
                "Library context."
            ),
            (
                "According to your enabled reference strategy library, "
                "you have one strategy currently enabled: "
                "Simple Moving Average Crossover."
            ),
            intent="trading_conversation",
            symbol=None,
            request_route="strategy_library_identity",
            owner_user_id="test-owner",
        )

    assert result is None

    assert list(
        tmp_path.glob(
            "candidate_*.json"
        )
    ) == []



def test_strategy_library_list_and_count_routes_never_create_candidates(
    tmp_path,
) -> None:

    with patch(
        "backend.app.stacks.chat_public.strategy_proposal_capture."
        "OUT_DIR",
        tmp_path,
    ):

        for route in (
            "strategy_library_list",
            "strategy_library_count",
        ):

            result = capture_strategy_proposal(
                "What strategies are enabled in my Strategy Library?",
                "Simple Moving Average Crossover.",
                intent="trading_conversation",
                symbol=None,
                request_route=route,
                owner_user_id="test-owner",
            )

            assert result is None

    assert list(
        tmp_path.glob(
            "candidate_*.json"
        )
    ) == []



def test_financial_strategy_intent_remains_eligible(
    tmp_path,
) -> None:
    with patch(
        "backend.app.stacks.chat_public.strategy_proposal_capture."
        "OUT_DIR",
        tmp_path,
    ):
        result = capture_strategy_proposal(
            "Create an RSI strategy for AAPL.",
            "Use an RSI entry and stop-loss.",
            intent="trading_conversation",
            symbol="AAPL",
            owner_user_id="test-owner",
        )

    assert result is not None
    assert result["captured"] is True
    assert result["symbol"] == "AAPL"
    assert result["status"] == "captured_pending_review"
