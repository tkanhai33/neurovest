from unittest.mock import patch

from backend.app.stacks.chat_public.developer_self_review import (
    render_review,
)
from backend.app.stacks.chat_public.developer_self_review_ai import (
    _valid_ai_recommendations,
)


def test_accepts_exact_line_evidence():
    source = ["def example():", "    return 123"]
    raw = {"recommendations": [{
        "line": 2,
        "evidence": "return 123",
        "suggested_change": "Validate the result.",
        "expected_benefit": "Rejects invalid return values before downstream use.",
        "risk": "May change accepted results; test valid and invalid cases.",
    }]}
    assert len(_valid_ai_recommendations(raw, source)) == 1


def test_rejects_invented_evidence():
    raw = {"recommendations": [{
        "line": 1,
        "evidence": "not real source",
        "suggested_change": "Change logic.",
        "expected_benefit": "Better correctness.",
        "risk": "Regression risk.",
    }]}
    assert _valid_ai_recommendations(raw, ["def example():"]) == []


def test_model_failure_preserves_static_review():
    with patch(
        "backend.app.stacks.chat_public.developer_self_review_ai."
        "_ollama_recommendations",
        side_effect=TimeoutError(),
    ):
        response = render_review("developer_repository_inspection")

    assert "Function Self-Review" in response
    assert "Local model review unavailable" in response


def test_ai_results_appear_inside_existing_review():
    findings = [{
        "line": 25,
        "evidence": "def inspect_repository",
        "change": "Extract ranking logic.",
        "benefit": "Easier targeted testing.",
        "risk": "Preserve search relevance.",
    }]
    with patch(
        "backend.app.stacks.chat_public.developer_self_review_ai."
        "_ollama_recommendations",
        return_value=findings,
    ):
        response = render_review("developer_repository_inspection")

    assert "Function Self-Review" in response
    assert "Local AI functional improvement" in response
    assert "Extract ranking logic" in response
