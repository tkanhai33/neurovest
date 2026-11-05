from backend.app.stacks.chat_public.answer_relevance_3dr2 import (
    assess,
    eligible,
)


TECHNICAL_QUESTIONS = (
    "In a hypothetical application, explain tradeoffs for Redis caching consistency.",
    "In a hypothetical application, explain rollback approach for FastAPI validation.",
    "In a hypothetical application, explain failure handling for PostgreSQL transactions.",
    "In a hypothetical application, explain test strategy for HTTP idempotency.",
    "In a hypothetical application, explain minimal safe implementation for SQL query indexes.",
)


def test_software_technical_questions_skip_generic_overlap_gate():
    for question in TECHNICAL_QUESTIONS:
        result = assess(question, "An unrelated response with no matching terms.")
        assert eligible(question) is False
        assert result.checked is False
        assert result.reason == "outside_scope"


def test_general_explanation_remains_in_relevance_gate():
    question = "Explain how the water cycle works."
    answer = "The water cycle moves water through evaporation and precipitation."
    result = assess(question, answer)

    assert eligible(question) is True
    assert result.checked is True
    assert result.relevant is True
