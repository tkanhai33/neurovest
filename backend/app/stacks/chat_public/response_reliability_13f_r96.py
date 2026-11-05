"""
NeuroVest R96 — final answer reliability decisions.

Pure advisory and classification functions.
No external calls, database access, execution or authorization.
"""

from __future__ import annotations

import re

# NEUROVEST_R96_RELIABILITY_ENGINE

MAX_MESSAGE = 50000

PROTECTED = re.compile(
    r"\b("
    r"developer authorization|developer role|"
    r"account permissions|broker order|"
    r"execute trade|live trading|"
    r"portfolio holdings|private account|"
    r"emergency stop|emergency_stop"
    r")\b",
    re.IGNORECASE,
)

RETRY_MESSAGE = (
    "I couldn't complete that response reliably. "
    "Please retry your request. I haven't verified "
    "an answer and won't invent one."
)


def classify_response(question, answer):
    """Classify without modifying an authorized answer."""

    if not isinstance(question, str):
        question = ""

    protected = bool(PROTECTED.search(question))

    if not isinstance(answer, str):
        state = "non_string"
    elif not answer.strip():
        state = "empty"
    elif len(answer) > MAX_MESSAGE:
        state = "oversize"
    else:
        state = "present"

    return {
        "state": state,
        "protected": protected,
        "needs_recovery": state in ("empty", "non_string"),
        "safe_recovery_candidate": (
            state in ("empty", "non_string")
            and not protected
        ),
        "answer_length": (
            len(answer) if isinstance(answer, str) else 0
        ),
    }


def recovery_candidate(question, answer):
    decision = classify_response(question, answer)

    if decision["safe_recovery_candidate"]:
        return RETRY_MESSAGE, decision

    return answer, decision


def quality_summary(assessment):
    """Bounded diagnostics, never expose raw user content."""

    requested = getattr(assessment, "requested", ())
    missing = getattr(assessment, "missing", ())

    return {
        "status": str(
            getattr(assessment, "confidence", "unknown")
        )[:64],
        "requested_count": len(requested),
        "missing_count": len(missing),
        "missing_components": [
            str(item)[:32] for item in list(missing)[:12]
        ],
        "incomplete_code": bool(
            getattr(assessment, "truncated_code_fence", False)
        ),
        "incomplete_table": bool(
            getattr(assessment, "incomplete_table", False)
        ),
        "evidence_requested": bool(
            getattr(assessment, "evidence_requested", False)
        ),
        "source_markers_present": bool(
            getattr(assessment, "source_markers_present", False)
        ),
        "evidence_verified": False,
    }
