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


NEURO_FAST_MODEL = "neuro-fast-no-think:latest"
NEURO_REASON_MODEL = "neuro-reason:latest"
NEURO_CODE_MODEL = NEURO_REASON_MODEL
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
            r"derivative|differentiate|integral|integrate|"
            r"limit|determinant|matrix|percentage|percent"
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
        r"\b(code|coding|python|typescript|javascript|sql|fastapi|asyncio|async|await)\b",
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
            r"research|investigate|look up|"
            r"find (?:sources?|papers?|evidence)|"
            r"scientific papers?|academic papers?|"
            r"cite (?:the )?sources?|with citations|"
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
    re.compile(
        (
            r"\b("
            r"concentration risk|"
            r"value investing|growth investing|"
            r"momentum investing|factor investing|"
            r"systematic risk|company-specific risk|"
            r"market-wide risk|asset allocation|"
            r"backtesting|strategy evaluation"
            r")\b"
        ),
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


def _nv12c_original_route_cognitive_request(
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

    contains_personal_context = bool(
        re.search(
            r"\b(my|mine|account|accounts|holding|holdings|"
            r"position|positions|balance|broker)\b",
            normalized_message,
            re.I,
        )
    )

    requires_current_fact = bool(
        re.search(
            r"\b(current|latest|today|now|price|quote|"
            r"news|headline|headlines)\b",
            normalized_message,
            re.I,
        )
    )

    educational_explanation = bool(
        re.match(
            r"^(?:explain(?:\s+(?:the|basic))?|how does)\b",
            normalized_message,
            re.I,
        )
        and not re.search(
            r"\b(?:analyze|analysis|compare|evaluate|critique|"
            r"explain why|create|design|develop|underperform|"
            r"strategy)\b",
            normalized_message,
            re.I,
        )
    )

    generic_education_fast_path = (
        (not reason_required or educational_explanation)
        and not deterministic_tool_required
        and not code_required
        and not contains_personal_context
        and not requires_current_fact
        and family in {
            "GENERAL",
            "MARKET",
            "PORTFOLIO",
        }
    )

    if generic_education_fast_path:
        return CognitiveRoutingDecision(
            tier="fast",
            model=NEURO_FAST_MODEL,
            reason=(
                "Generic educational questions use the "
                "low-latency local model. Personal, current-data, "
                "code, and deterministic-math requests keep their "
                "specialized paths."
            ),
            intent=intent_name,
            family=family,
            subtype=subtype,
            deterministic_tool_required=False,
            retrieval_required=retrieval_required,
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


# NEUROVEST_ADAPTIVE_COGNITION_12C
#
# Conservative escalation of EXISTING fast-model decisions.
# This is not an authorization layer or a replacement router.
# Developer commands and execution authority remain unchanged.

def _nv12c_route_target(message):
    import re as _nv12c_re

    text = str(message or "").strip().lower()

    if not text or len(text) > 12000:
        return None

    # Never reinterpret privileged or execution-oriented requests.
    protected = (
        "what do you need to improve",
        "developer command",
        "emergency_stop",
        "emergency stop",
        "live trading",
        "place an order",
        "execute an order",
        "submit an order",
        "broker execution",
        "withdraw funds",
        "admin command",
        "admin_control",
    )

    if any(term in text for term in protected):
        return None

    coding = (
        "debug this",
        "debug my",
        "fix this code",
        "fix my code",
        "traceback",
        "stack trace",
        "refactor this",
        "refactor my",
        "implement a",
        "implement the",
        "write a complete function",
        "write a complete class",
        "write a complete script",
        "unit tests for",
        "code review",
        "review this code",
        "python exception",
        "typescript error",
        "javascript error",
        "sql query optimization",
    )

    if any(term in text for term in coding):
        return "qwen3-coder:latest"

    # A pasted exception plus source-like content.
    if (
        ("exception:" in text or "error:" in text)
        and any(
            term in text
            for term in (
                "python",
                "javascript",
                "typescript",
                "function ",
                "def ",
                "class ",
                "traceback",
            )
        )
    ):
        return "qwen3-coder:latest"

    reasoning = (
        "analyze in depth",
        "compare the tradeoffs",
        "compare the pros and cons",
        "root cause analysis",
        "derive the",
        "prove that",
        "step-by-step reasoning",
        "multi-step analysis",
        "design a system",
        "evaluate the evidence",
        "assess the risks",
        "compare these strategies",
        "portfolio optimization",
        "stress test the portfolio",
        "explain the reasoning behind",
        "construct a detailed plan",
    )

    if any(term in text for term in reasoning):
        return "neuro-reason:latest"

    # Multiple explicit constraints often deserve deeper handling,
    # but length alone must not escalate ordinary conversations.
    if (
        len(text) >= 350
        and len(
            _nv12c_re.findall(
                r"\b(?:first|second|third|then|"
                r"however|because|unless|while|"
                r"constraint|tradeoff|scenario)\b",
                text,
            )
        ) >= 3
    ):
        return "neuro-reason:latest"

    return None


def _nv12c_read_message(args, kwargs):
    import inspect as _nv12c_inspect

    original = _nv12c_original_route_cognitive_request

    try:
        bound = _nv12c_inspect.signature(
            original
        ).bind_partial(*args, **kwargs)
    except (TypeError, ValueError):
        return None

    for key in (
        "message",
        "user_message",
        "current_message",
        "prompt",
        "request",
    ):
        value = bound.arguments.get(key)

        if isinstance(value, str):
            return value

        if value is not None:
            nested = getattr(value, "message", None)
            if isinstance(nested, str):
                return nested

    return None


def _nv12c_upgrade_decision(decision, target):
    import copy as _nv12c_copy
    import dataclasses as _nv12c_dataclasses

    if not target or decision is None:
        return decision

    existing = getattr(decision, "model", None)

    # Never override a reasoning/coding choice already made
    # by the production cognitive router.
    if existing not in (
        "neuro-fast",
        "neuro-fast:latest",
        "neuro-fast-no-think",
        "neuro-fast-no-think:latest",
    ):
        return decision

    if _nv12c_dataclasses.is_dataclass(decision):
        return _nv12c_dataclasses.replace(
            decision,
            model=target,
        )

    if isinstance(decision, tuple) and hasattr(
        decision, "_replace"
    ):
        return decision._replace(model=target)

    if hasattr(decision, "model_copy"):
        return decision.model_copy(
            update={"model": target}
        )

    if hasattr(decision, "copy") and hasattr(
        decision, "model_fields"
    ):
        return decision.copy(
            update={"model": target}
        )

    if hasattr(decision, "__dict__"):
        replacement = _nv12c_copy.copy(decision)
        replacement.model = target
        return replacement

    # Unknown decision type: do not override it.
    return decision


def route_cognitive_request(*args, **kwargs):
    message = _nv12c_read_message(args, kwargs)

    decision = _nv12c_original_route_cognitive_request(
        *args, **kwargs
    )

    target = _nv12c_route_target(message)

    return _nv12c_upgrade_decision(
        decision,
        target,
    )



# NEUROVEST_G43_R41E_REASONING_SELECTION
# Opt-in selection enhancement; default disabled.
import os as _nv_r41e_os

_nv_r41e_previous_route = route_cognitive_request

def route_cognitive_request(*args, **kwargs):
    decision = _nv_r41e_previous_route(*args, **kwargs)

    if _nv_r41e_os.environ.get(
        "NV_R41E_REASONING_ENABLED", ""
    ) != "1":
        return decision

    message = kwargs.get(
        "message",
        args[0] if args else None,
    )

    from backend.app.stacks.chat_public.reasoning_selection_r41e import (
        upgrade_reasoning_decision,
    )

    return upgrade_reasoning_decision(message, decision)


# NEUROVEST_G43_R42A_ALIGNMENT
import os as _r42a_router_os

_r42a_previous_route = route_cognitive_request

def route_cognitive_request(*args, **kwargs):
    decision = _r42a_previous_route(*args, **kwargs)
    if _r42a_router_os.environ.get("NV_R42A_ALIGNMENT_ENABLED") != "1":
        return decision
    message = kwargs.get("message", args[0] if args else None)
    from backend.app.stacks.chat_public.routing_alignment_r42a import align_cognitive
    return align_cognitive(message, decision)
