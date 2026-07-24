"""
Canonical NeuroVest cognitive model router.

This module selects a model and future cognitive requirements.
It performs no inference, retrieval, calculation, persistence,
account mutation, order placement, broker access, or live trading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Protocol


ModelTier = Literal[
    "fast",
    "reason",
    "code",
    "fallback",
]


NEURO_FAST_MODEL = "neuro-fast:latest"
NEURO_REASON_MODEL = "neuro-reason:latest"
NEURO_CODE_MODEL = "qwen3-coder:latest"
NEURO_FALLBACK_MODEL = "llama3.1:latest"


class IntentLike(Protocol):
    intent: str
    family: str
    subtype: str
    developer_mode: bool
    requires_repo_context: bool
    requires_architecture_context: bool


@dataclass(
    frozen=True,
    slots=True,
)
class CognitiveRoutingDecision:
    tier: ModelTier
    model: str
    reason: str
    intent: str
    family: str
    subtype: str
    deterministic_tool_required: bool
    retrieval_required: bool
    fallback_model: str

    def as_dict(
        self,
    ) -> dict[str, object]:
        return {
            "tier": self.tier,
            "model": self.model,
            "reason": self.reason,
            "intent": self.intent,
            "family": self.family,
            "subtype": self.subtype,
            "deterministic_tool_required": (
                self.deterministic_tool_required
            ),
            "retrieval_required": (
                self.retrieval_required
            ),
            "fallback_model": (
                self.fallback_model
            ),
        }


_MATH_PATTERNS = (
    re.compile(
        (
            r"\b("
            r"calculate|compute|solve|equation|arithmetic|"
            r"percentage|percent"
            r")\b"
        ),
        re.I,
    ),
    re.compile(
        r"\b(profit|loss|pnl|return|drawdown|cost basis|compound)\b",
        re.I,
    ),
    re.compile(
        r"\b(position size|allocation|risk reward|risk/reward)\b",
        re.I,
    ),
    re.compile(
        r"(?:\d+(?:\.\d+)?)\s*[%+\-*/=]",
        re.I,
    ),
    re.compile(
        (
            r"\bwhat\s+is\s+"
            r"[-+]?\d+(?:\.\d+)?\s+percent\s+of\s+"
            r"[-+]?\d+(?:\.\d+)?\b"
        ),
        re.I,
    ),
)


_CODE_PATTERNS = (
    re.compile(
        r"\b(code|coding|python|typescript|javascript|sql|fastapi)\b",
        re.I,
    ),
    re.compile(
        r"\b(debug|refactor|repository|codebase|function|class|endpoint)\b",
        re.I,
    ),
    re.compile(
        r"\b(traceback|exception|syntax error|compile error|pytest)\b",
        re.I,
    ),
)


_REASON_PATTERNS = (
    re.compile(
        r"\b(analyze|analysis|compare|evaluate|critique|explain why)\b",
        re.I,
    ),
    re.compile(
        r"\b(strategy|portfolio|market|stock|risk|investment|trading)\b",
        re.I,
    ),
    re.compile(
        r"\b(create|design|develop)\b.*\b(strategy|plan|framework)\b",
        re.I,
    ),
)


_RETRIEVAL_PATTERNS = (
    re.compile(
        r"\b(current|latest|today|recent|news|price|quote|market data)\b",
        re.I,
    ),
    re.compile(
        r"\b(my portfolio|my positions|my orders|my account)\b",
        re.I,
    ),
    re.compile(
        r"\b(repository|codebase|architecture|neurovest)\b",
        re.I,
    ),
    re.compile(
        (
            r"\b("
            r"local research library|research library|"
            r"academic research|research paper|research papers|"
            r"source citation|source citations|"
            r"approved citation|approved citations"
            r")\b"
        ),
        re.I,
    ),
    re.compile(
        r"\b(fama[\s\-–—]*french|ssrn)\b",
        re.I,
    ),
)


def _matches(
    patterns: tuple[re.Pattern[str], ...],
    message: str,
) -> bool:
    return any(
        pattern.search(
            message
        )
        for pattern in patterns
    )


def route_cognitive_request(
    message: str,
    *,
    intent: IntentLike,
) -> CognitiveRoutingDecision:
    """
    Return one immutable routing decision.

    The router declares future tool and retrieval requirements but
    does not execute either capability. Those stages remain locked
    until their dedicated Objective 4 qualification.
    """

    normalized_message = str(
        message
    ).strip()

    intent_name = str(
        getattr(
            intent,
            "intent",
            "general_conversation",
        )
        or "general_conversation"
    )

    family = str(
        getattr(
            intent,
            "family",
            "GENERAL",
        )
        or "GENERAL"
    ).upper()

    subtype = str(
        getattr(
            intent,
            "subtype",
            "discussion",
        )
        or "discussion"
    )

    deterministic_tool_required = _matches(
        _MATH_PATTERNS,
        normalized_message,
    )

    retrieval_required = bool(
        getattr(
            intent,
            "requires_repo_context",
            False,
        )
        or getattr(
            intent,
            "requires_architecture_context",
            False,
        )
        or _matches(
            _RETRIEVAL_PATTERNS,
            normalized_message,
        )
        or family == "STRATEGY"
    )

    code_required = bool(
        getattr(
            intent,
            "developer_mode",
            False,
        )
        or family == "DEVELOPER"
        or _matches(
            _CODE_PATTERNS,
            normalized_message,
        )
    )

    reason_required = bool(
        family
        in {
            "MARKET",
            "PORTFOLIO",
            "STRATEGY",
        }
        or intent_name
        == "trading_conversation"
        or deterministic_tool_required
        or retrieval_required
        or _matches(
            _REASON_PATTERNS,
            normalized_message,
        )
    )

    if code_required:
        return CognitiveRoutingDecision(
            tier="code",
            model=NEURO_CODE_MODEL,
            reason=(
                "Developer, repository, architecture, "
                "or coding work requires the code model."
            ),
            intent=intent_name,
            family=family,
            subtype=subtype,
            deterministic_tool_required=(
                deterministic_tool_required
            ),
            retrieval_required=(
                retrieval_required
            ),
            fallback_model=(
                NEURO_FALLBACK_MODEL
            ),
        )

    if reason_required:
        return CognitiveRoutingDecision(
            tier="reason",
            model=NEURO_REASON_MODEL,
            reason=(
                "Market, portfolio, strategy, math, retrieval, "
                "or analytical work requires deeper reasoning."
            ),
            intent=intent_name,
            family=family,
            subtype=subtype,
            deterministic_tool_required=(
                deterministic_tool_required
            ),
            retrieval_required=(
                retrieval_required
            ),
            fallback_model=(
                NEURO_FALLBACK_MODEL
            ),
        )

    return CognitiveRoutingDecision(
        tier="fast",
        model=NEURO_FAST_MODEL,
        reason=(
            "General conversational work is routed "
            "to the low-latency model."
        ),
        intent=intent_name,
        family=family,
        subtype=subtype,
        deterministic_tool_required=False,
        retrieval_required=False,
        fallback_model=(
            NEURO_FALLBACK_MODEL
        ),
    )
