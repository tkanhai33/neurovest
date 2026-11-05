from backend.app.stacks.chat_public.developer_self_review_ai import (
    _valid_ai_recommendations,
)

LINES = [
    "def inspect_repository(query, max_files=5):",
    "    if path.stat().st_size > 180_000:",
    "        continue",
    "    return sorted(results, key=lambda x: x.score)",
]


def make(line, evidence, change, benefit, risk):
    return {"recommendations": [{
        "line": line,
        "evidence": evidence,
        "suggested_change": change,
        "expected_benefit": benefit,
        "risk": risk,
    }]}


def test_rejects_no_risk():
    raw = make(
        4, "return sorted(results",
        "Use a deterministic ranking tie breaker.",
        "Equal score results have a stable ordering.",
        "None",
    )
    assert _valid_ai_recommendations(raw, LINES) == []


def test_rejects_default_increase():
    raw = make(
        1, "max_files=5",
        "Change max_files = 10.",
        "Returns more results to the caller.",
        "Potential latency increase; test response duration.",
    )
    assert _valid_ai_recommendations(raw, LINES) == []


def test_rejects_file_size_increase():
    raw = make(
        2, "path.stat().st_size > 180_000",
        "Change st_size > 180_000 to st_size > 200_000.",
        "Larger modules become eligible for scanning.",
        "Memory may increase; regression test size limits.",
    )
    assert _valid_ai_recommendations(raw, LINES) == []


def test_requires_verification():
    raw = make(
        4, "return sorted(results",
        "Add filename to ranking ties.",
        "Equal score results sort consistently.",
        "Output ordering may change unexpectedly.",
    )
    assert _valid_ai_recommendations(raw, LINES) == []


def test_accepts_testable_recommendation():
    raw = make(
        4, "return sorted(results",
        "Add filename to ranking ties.",
        "Equal score results sort consistently.",
        "Ordering may change; regression test tied scores.",
    )
    assert len(_valid_ai_recommendations(raw, LINES)) == 1
