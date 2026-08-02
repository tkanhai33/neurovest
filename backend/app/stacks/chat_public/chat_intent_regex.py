from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatIntent:
    """
    Backward-compatible intent result enriched with V2 metadata.

    The legacy ``intent`` value remains the runtime routing contract.
    New metadata may be consumed by later Neuro Chat Engine V2 stages.
    """

    intent: str
    symbol: str | None = None
    blocked: bool = False

    family: str = "GENERAL"
    subtype: str = "discussion"
    confidence: float = 0.5

    developer_mode: bool = False
    architecture_mode: bool = False
    self_evaluation: bool = False
    requires_repo_context: bool = False
    requires_architecture_context: bool = False


COMMAND_PATTERNS = {
    "graph_reset": re.compile(
        r"^\s*(graph[_\s-]?reset)\s*$",
        re.I,
    ),
    "graph_validate": re.compile(
        r"^\s*(graph[_\s-]?validate)\s*$",
        re.I,
    ),
    "simulate_trade": re.compile(
        r"^\s*(simulate[_\s-]?trade)\s+"
        r"([A-Z][A-Z0-9.\-]{0,12})\s*$",
        re.I,
    ),
}


BLOCKED_PATTERNS = [
    re.compile(
        r"\b(place|send|execute|submit)\b"
        r".*\b(live|real)\b"
        r".*\b(order|trade|buy|sell)\b",
        re.I,
    ),
    re.compile(
        r"\b(turn on|enable)\b"
        r".*\b(live trading|broker execution|real orders)\b",
        re.I,
    ),
]


GREETING_PATTERNS = [
    re.compile(
        r"^\s*(hello|hi|hey|good morning|good afternoon|"
        r"good evening)\b[!?.\s]*$",
        re.I,
    ),
]


PERSONALITY_PATTERNS = [
    re.compile(
        r"\b(are you happy|are you a happy wolf|are you a wolf|"
        r"who are you|tell me about yourself|how are you feeling)\b",
        re.I,
    ),
]


SELF_EVALUATION_PATTERNS = [
    re.compile(
        r"\b(how can (i|we) improve you|evaluate yourself|"
        r"review yourself|what are your limitations|"
        r"what capabilities are missing|what are you missing)\b",
        re.I,
    ),
]


ARCHITECTURE_PATTERNS = [
    re.compile(
        r"\b(review|evaluate|inspect|explain|assess)\b"
        r".*\b(architecture|repository|codebase|system design)\b",
        re.I,
    ),
    re.compile(
        r"\b(architecture review|repository review|"
        r"review the architecture|review the repository)\b",
        re.I,
    ),
]




SOFTWARE_DEBUG_REQUEST_PATTERN = re.compile(
    r"\b("
    r"debug(?:ging)?|traceback|stack trace|exception|"
    r"http\s*5\d\d|server error"
    r")\b"
    r".*\b("
    r"fastapi|python|typescript|javascript|endpoint|api|"
    r"function|class|route|handler"
    r")\b"
    r"|"
    r"\b("
    r"fastapi|python|typescript|javascript|endpoint"
    r")\b"
    r".*\b("
    r"debug(?:ging)?|traceback|exception|http\s*5\d\d|"
    r"server error"
    r")\b",
    re.I,
)


RESEARCH_PATTERNS = (
    re.compile(
        r"\b(ssrn|research|paper|papers|journal|citation|citations|academic|knowledge|corpus|document)\b",
        re.I,
    ),
)

DEVELOPER_PATTERNS = [
    re.compile(
        r"\b(as your developer|as (?:the )?authenticated developer|developer mode|"
        r"how should neurovest evolve|"
        r"what should we build next|"
        r"what should i build next|"
        r"help me improve neurovest)\b",
        re.I,
    ),
]


SYSTEM_PATTERNS = [
    (
        "diagnostics",
        re.compile(
            r"\b(system diagnostics|run diagnostics|diagnostic status)\b",
            re.I,
        ),
    ),
    (
        "runtime_status",
        re.compile(
            r"\b(runtime status|system status|service health|"
            r"runtime health)\b",
            re.I,
        ),
    ),
]


PORTFOLIO_PATTERNS = [
    re.compile(
        r"\b(portfolio|holdings|allocation|positions?|"
        r"cost basis|profit and loss|pnl)\b",
        re.I,
    ),
]


TRADING_PATTERNS = [
    re.compile(
        r"\b(should i|do we|would you)\b"
        r".*\b(buy|sell|hold|trade)\b",
        re.I,
    ),
    re.compile(
        r"\b(price|market|strategy|risk|stock|ticker|"
        r"fundamental|technical analysis)\b",
        re.I,
    ),
]


# Common uppercase words that are not ticker symbols.
_SYMBOL_EXCLUSIONS = {
    "A",
    "AI",
    "AM",
    "AN",
    "AND",
    "ARE",
    "AS",
    "AT",
    "BE",
    "BY",
    "CAN",
    "DO",
    "FOR",
    "FROM",
    "GO",
    "HOW",
    "I",
    "IF",
    "IN",
    "IS",
    "IT",
    "MY",
    "NO",
    "OF",
    "ON",
    "OR",
    "SO",
    "THE",
    "TO",
    "UP",
    "US",
    "WE",
    "WHAT",
    "WHO",
    "WHY",
    "YES",
    "YOU",
    "SSRN",
}


def _extract_symbol(message: str) -> str | None:
    for match in re.finditer(
        r"\b([A-Z]{1,5}(?:\.TO)?)\b",
        message,
    ):
        candidate = match.group(1).upper()

        if candidate not in _SYMBOL_EXCLUSIONS:
            return candidate

    return None


TRAINING_SESSION_PATTERN = re.compile(
    r"\b(?:run|start|begin|launch)\b"
    r".{0,80}\btraining\s+session\b"
    r".{0,100}\b(?:canadian|canada|tsx)\b",
    re.IGNORECASE,
)

TRAINING_DURATION_PATTERN = re.compile(
    r"\b(\d{1,3})\s*"
    r"(second|seconds|minute|minutes)\b",
    re.IGNORECASE,
)


def detect_chat_intent(message: str) -> ChatIntent:
    clean = message.strip()

    # Safety remains the highest-priority deterministic boundary.
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="blocked_live_execution",
                blocked=True,
                family="SAFETY",
                subtype="blocked_live_execution",
                confidence=1.0,
            )


    training_match = (
        TRAINING_SESSION_PATTERN.search(
            clean
        )
    )

    if training_match:
        duration_seconds = 120

        duration_match = (
            TRAINING_DURATION_PATTERN.search(
                clean
            )
        )

        if duration_match:
            amount = int(
                duration_match.group(1)
            )

            unit = (
                duration_match.group(2)
                .lower()
            )

            duration_seconds = (
                amount * 60
                if unit.startswith(
                    "minute"
                )
                else amount
            )

        return ChatIntent(
            intent="run_training_session",
            family="TRAINING",
            subtype="bounded_canadian_training",
            confidence=1.0,
        )

    # Existing runtime commands retain their exact legacy intent strings.
    for intent_name, pattern in COMMAND_PATTERNS.items():
        match = pattern.search(clean)

        if not match:
            continue

        symbol = None

        if (
            intent_name == "simulate_trade"
            and match.lastindex
            and match.lastindex >= 2
        ):
            symbol = match.group(2).upper()

        return ChatIntent(
            intent=intent_name,
            symbol=symbol,
            family=(
                "SYSTEM"
                if intent_name in {"graph_reset", "graph_validate"}
                else "MARKET"
            ),
            subtype=intent_name,
            confidence=1.0,
        )

    # Developer/self-evaluation checks must run before market detection.
    for pattern in SELF_EVALUATION_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="DEVELOPER",
                subtype="self_evaluation",
                confidence=1.0,
                developer_mode=True,
                self_evaluation=True,
                requires_repo_context=True,
                requires_architecture_context=True,
            )

    for pattern in ARCHITECTURE_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="DEVELOPER",
                subtype="architecture_review",
                confidence=1.0,
                developer_mode=True,
                architecture_mode=True,
                requires_repo_context=True,
                requires_architecture_context=True,
            )

    for pattern in DEVELOPER_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="DEVELOPER",
                subtype="developer_review",
                confidence=1.0,
                developer_mode=True,
                requires_repo_context=True,
                requires_architecture_context=True,
            )

    # Explicit software-debugging requests must not be redirected by
    # broad financial terms such as API, route, risk, or endpoint.
    if SOFTWARE_DEBUG_REQUEST_PATTERN.search(clean):
        return ChatIntent(
            intent="general_conversation",
            family="DEVELOPER",
            subtype="software_debugging",
            confidence=1.0,
            developer_mode=True,
        )

    for subtype, pattern in SYSTEM_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="SYSTEM",
                subtype=subtype,
                confidence=1.0,
            )

    for pattern in GREETING_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="GENERAL",
                subtype="greeting",
                confidence=1.0,
            )

    for pattern in PERSONALITY_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="general_conversation",
                family="GENERAL",
                subtype="personality",
                confidence=1.0,
            )


    for pattern in RESEARCH_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="research_conversation",
                family="RESEARCH",
                subtype="knowledge_lookup",
                confidence=1.0,
            )

    for pattern in PORTFOLIO_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="trading_conversation",
                symbol=_extract_symbol(clean),
                family="PORTFOLIO",
                subtype="portfolio_review",
                confidence=1.0,
            )

    symbol = _extract_symbol(clean)

    for pattern in TRADING_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(
                intent="trading_conversation",
                symbol=symbol,
                family="MARKET",
                subtype="market_analysis",
                confidence=1.0,
            )

    # A valid explicit ticker is also treated as market discussion.
    if symbol is not None:
        return ChatIntent(
            intent="trading_conversation",
            symbol=symbol,
            family="MARKET",
            subtype="stock_lookup",
            confidence=1.0,
        )

    return ChatIntent(
        intent="general_conversation",
        family="GENERAL",
        subtype="discussion",
        confidence=0.5,
    )


__all__ = [
    "ChatIntent",
    "detect_chat_intent",
]
