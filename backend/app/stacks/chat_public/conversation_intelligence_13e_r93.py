"""
NeuroVest R93 — Integrated conversation-intelligence foundation.

Responsibilities:
  - Normalize bounded conversation history
  - Resolve supported follow-up references
  - Decompose explicit user deliverables
  - Assess evidence availability
  - Assess answer completeness
  - Produce structured, non-authoritative guidance

Not responsible for:
  - Authenticating or authorizing users
  - Executing trading orders
  - Inventing retrieval evidence
  - Overriding model or tool routing
  - Persisting conversation history

All assessments are advisory until explicitly integrated
with the existing trusted chat runtime.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

# NEUROVEST_R93_INTEGRATED_CONVERSATION_INTELLIGENCE

MAX_HISTORY = 12
MAX_MESSAGE = 6000
MAX_ANSWER = 50000

REFERENCE_PATTERN = re.compile(
    r"\b("
    r"that|those|them|it|its|their|"
    r"previous|earlier|above|"
    r"the first|the second|"
    r"same approach|same example|"
    r"what about|how about"
    r")\b",
    re.IGNORECASE,
)

PROTECTED_PATTERN = re.compile(
    r"\b("
    r"developer authorization|developer role|"
    r"account permissions|broker order|"
    r"execute trade|live trading|"
    r"portfolio holdings|private account"
    r")\b",
    re.IGNORECASE,
)

REQUEST_RULES = (
    (
        "comparison",
        re.compile(
            r"\b(compare|comparison|versus|vs\.?)\b",
            re.I,
        ),
    ),
    (
        "example",
        re.compile(
            r"\b(example|demonstration|show how)\b",
            re.I,
        ),
    ),
    (
        "code",
        re.compile(
            r"\b(code|program|script|function)\b",
            re.I,
        ),
    ),
    (
        "steps",
        re.compile(
            r"\b(step.by.step|steps|instructions)\b",
            re.I,
        ),
    ),
    (
        "sources",
        re.compile(
            r"\b(cite|citations?|sources?|references?)\b",
            re.I,
        ),
    ),
    (
        "table",
        re.compile(
            r"\b(table|tabular)\b",
            re.I,
        ),
    ),
    (
        "risks",
        re.compile(
            r"\b(risks?|limitations?|drawbacks?)\b",
            re.I,
        ),
    ),
    (
        "recommendation",
        re.compile(
            r"\b(recommend|recommendation|best option)\b",
            re.I,
        ),
    ),
    (
        "summary",
        re.compile(
            r"\b(summarize|summary|takeaways?)\b",
            re.I,
        ),
    ),
)

SOURCE_PATTERN = re.compile(
    r"https?://[^\s<>]+|"
    r"\[[^\]]+\]\(https?://[^)]+\)|"
    r"\b(?:SEC EDGAR|CompanyFacts)\b",
    re.IGNORECASE,
)

CODE_FENCE = re.compile(
    r"(?m)^[ \t]{0,3}```"
)

TABLE_DIVIDER = re.compile(
    r"(?m)^\s*\|?\s*:?-{3,}:?"
    r"(?:\s*\|\s*:?-{3,}:?)+\s*\|?\s*$"
)

LIST_ENTRY = re.compile(
    r"(?m)^\s*(?:[-*+]|\d+[.)])\s+"
)


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class ConversationPlan:
    question: str
    effective_question: str
    follow_up: bool = False
    resolved_reference: bool = False
    context_available: bool = False
    context_used: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    protected: bool = False
    needs_clarification: bool = False
    evidence_requested: bool = False
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnswerAssessment:
    requested: list[str]
    present: list[str]
    missing: list[str]
    evidence_requested: bool
    source_markers_present: bool
    truncated_code_fence: bool
    incomplete_table: bool
    protected: bool
    confidence: str
    limitations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def normalize_history(
    history: Any,
) -> list[Turn]:
    """Accept bounded, explicitly supplied conversation turns."""

    if not isinstance(history, (list, tuple)):
        return []

    result: list[Turn] = []

    for item in history[-MAX_HISTORY:]:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")

            if content is None:
                content = item.get("message")

        elif isinstance(item, Turn):
            role = item.role
            content = item.content

        else:
            continue

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()[:MAX_MESSAGE]

        if not content:
            continue

        result.append(
            Turn(role=role, content=content)
        )

    return result


def requested_deliverables(
    question: str,
) -> list[str]:
    if not isinstance(question, str):
        return []

    return [
        name
        for name, pattern in REQUEST_RULES
        if pattern.search(question)
    ]


def _last_user_turn(
    history: list[Turn],
) -> str | None:
    for item in reversed(history):
        if item.role == "user":
            return item.content
    return None


def _last_assistant_turn(
    history: list[Turn],
) -> str | None:
    for item in reversed(history):
        if item.role == "assistant":
            return item.content
    return None


def plan_conversation(
    question: str,
    history: Any = None,
    evidence_available: bool = False,
) -> ConversationPlan:

    if not isinstance(question, str):
        question = ""

    question = question.strip()[:MAX_MESSAGE]

    turns = normalize_history(history)

    protected = bool(
        PROTECTED_PATTERN.search(question)
    )

    reference = bool(
        REFERENCE_PATTERN.search(question)
    )

    previous_user = _last_user_turn(turns)
    previous_assistant = _last_assistant_turn(turns)

    context_available = bool(
        previous_user or previous_assistant
    )

    # Never pretend to resolve a missing antecedent.
    resolved_reference = (
        reference and context_available
    )

    effective = question
    context_used: list[str] = []
    warnings: list[str] = []

    if reference and previous_user:
        context_used.append("previous_user")

    if reference and previous_assistant:
        context_used.append("previous_assistant")

    if reference and not context_available:
        warnings.append(
            "The follow-up references earlier context "
            "that was not supplied."
        )

    # Preserve the actual latest user request.
    # Add context as separately labeled dialogue,
    # not as fabricated replacement user text.
    if resolved_reference and not protected:
        snippets = []

        if previous_user:
            snippets.append(
                "Earlier user request:\n"
                + previous_user[:2000]
            )

        if previous_assistant:
            snippets.append(
                "Earlier assistant response:\n"
                + previous_assistant[:2000]
            )

        effective = (
            "\n\n".join(snippets)
            + "\n\nCurrent user follow-up:\n"
            + question
        )

    deliverables = requested_deliverables(question)

    # A follow-up may inherit previously requested
    # output requirements, but never their authority.
    if resolved_reference and previous_user:
        for item in requested_deliverables(previous_user):
            if item not in deliverables:
                deliverables.append(item)

    if protected:
        effective = question
        context_used = []

    return ConversationPlan(
        question=question,
        effective_question=effective,
        follow_up=reference,
        resolved_reference=resolved_reference,
        context_available=context_available,
        context_used=context_used,
        deliverables=deliverables,
        protected=protected,
        needs_clarification=(
            reference and not context_available
        ),
        evidence_requested="sources" in deliverables,
        warnings=warnings,
    )


def _has_table(answer: str) -> bool:
    return bool(TABLE_DIVIDER.search(answer))


def _has_comparison(answer: str) -> bool:
    return bool(
        _has_table(answer)
        or re.search(
            r"\b(whereas|compared with|"
            r"on the other hand|in contrast)\b",
            answer,
            re.I,
        )
    )


def _has_example(answer: str) -> bool:
    return bool(
        re.search(
            r"\b(for example|example:|"
            r"consider this|such as)\b",
            answer,
            re.I,
        )
        or CODE_FENCE.search(answer)
    )


def _detect_incomplete_table(
    answer: str,
) -> bool:
    lines = answer.splitlines()

    for index, line in enumerate(lines):
        if not TABLE_DIVIDER.match(line.strip()):
            continue

        if index == 0:
            return True

        header = lines[index - 1].strip()

        if not header or "|" not in header:
            return True

        expected = len(
            [cell for cell in header.split("|")
             if cell.strip()]
        )

        if expected < 2:
            continue

        for row in lines[index + 1:]:
            if not row.strip() or "|" not in row:
                break

            cells = len([
                cell for cell in row.split("|")
                if cell.strip()
            ])

            if cells < expected:
                return True

    return False


def assess_answer(
    question: str,
    answer: str,
    history: Any = None,
) -> AnswerAssessment:

    plan = plan_conversation(
        question,
        history,
    )

    requested = plan.deliverables

    if not isinstance(answer, str):
        answer = ""

    answer = answer[:MAX_ANSWER]

    present: list[str] = []
    missing: list[str] = []

    detectors = {
        "comparison": _has_comparison,
        "example": _has_example,
        "code": lambda a: bool(
            re.search(
                r"(?m)^\s*```[\w+-]*\s*$",
                a,
            )
        ),
        "steps": lambda a: bool(
            re.search(r"(?m)^\s*\d+[.)]\s", a)
        ),
        "sources": lambda a: bool(
            SOURCE_PATTERN.search(a)
        ),
        "table": _has_table,
        "risks": lambda a: bool(
            re.search(
                r"\b(risk|limitation|drawback|"
                r"trade-off|caution)\b",
                a,
                re.I,
            )
        ),
        "recommendation": lambda a: bool(
            re.search(
                r"\b(recommend|prefer|choose|"
                r"best option|suggest)\b",
                a,
                re.I,
            )
        ),
        "summary": lambda a: bool(
            re.search(
                r"\b(summary|takeaway|"
                r"in short|in conclusion)\b",
                a,
                re.I,
            )
        ),
    }

    for item in requested:
        detector = detectors.get(item)

        if detector and detector(answer):
            present.append(item)
        else:
            missing.append(item)

    unclosed_code = (
        len(CODE_FENCE.findall(answer)) % 2 != 0
    )

    incomplete_table = _detect_incomplete_table(
        answer
    )

    limitations: list[str] = []

    if missing:
        limitations.append(
            "Requested output components may be missing: "
            + ", ".join(missing)
        )

    if unclosed_code:
        limitations.append(
            "A Markdown code fence is not closed."
        )

    if incomplete_table:
        limitations.append(
            "A Markdown table may have incomplete rows."
        )

    source_markers = bool(
        SOURCE_PATTERN.search(answer)
    )

    if plan.evidence_requested and not source_markers:
        limitations.append(
            "The user requested evidence, but no "
            "source marker was found."
        )

    # Source presence is NOT source verification.
    if source_markers:
        limitations.append(
            "Source markers were detected; their "
            "contents have not been independently verified."
        )

    if unclosed_code or incomplete_table:
        confidence = "requires_review"
    elif missing:
        confidence = "potentially_incomplete"
    else:
        confidence = "structurally_complete"

    return AnswerAssessment(
        requested=requested,
        present=present,
        missing=missing,
        evidence_requested=plan.evidence_requested,
        source_markers_present=source_markers,
        truncated_code_fence=unclosed_code,
        incomplete_table=incomplete_table,
        protected=plan.protected,
        confidence=confidence,
        limitations=limitations,
    )


def evaluate_turn(
    question: str,
    answer: str,
    history: Any = None,
    evidence_available: bool = False,
) -> dict:
    """One bounded evaluation across the major capabilities."""

    plan = plan_conversation(
        question,
        history,
        evidence_available,
    )

    assessment = assess_answer(
        question,
        answer,
        history,
    )

    return {
        "version": "R93",
        "plan": plan.as_dict(),
        "assessment": assessment.as_dict(),
        "evidence_available": bool(evidence_available),
        "evidence_verified": False,
        "developer_authorization_granted": False,
        "tool_actions_executed": False,
        "live_trading_authorized": False,
    }
