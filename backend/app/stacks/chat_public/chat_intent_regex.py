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
        r"review yourself|where do you need improvement|"
        r"what are your limitations|"
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
    "EMA",
    # NEUROVEST_FINANCIAL_ACRONYM_GUARD_V1
    # ETF is normally a financial instrument category.
    # Do not infer a stock lookup from this acronym alone.
    "ETF",
    "FOR",
    "FROM",
    "GO",
    "HOW",
    "I",
    "IF",
    "IN",
    "IS",
    "IT",
    "MACD",
    "MY",
    "NO",
    "OF",
    "ON",
    "OR",
    "RSI",
    "SMA",
    "SO",
    "SSRN",
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
}


def _extract_symbol(message: str) -> str | None:
    for match in re.finditer(
        r"\b([A-Z]{1,5}(?:\.TO)?)\b",
        message,
    ):
        candidate = match.group(1).upper()

        # G41: TCP/UDP are networking terms in protocol questions.
        # Preserve explicit financial discussion rather than blocking
        # these names as market symbols globally.
        # G41: Interpret network protocol abbreviations in context.
        # Do not globally blacklist potentially legitimate tickers.
        network_context = bool(re.search(
            r"\b(?:protocols?|networking|transport|internet"
            r"|network|packet|routing|tcp\/ip|osi|web protocols?)\b",
            message,
            re.I,
        ))
        financial_context = bool(re.search(
            r"\b(?:ticker|stock|shares?|equity|quote|share price"
            r"|market cap|nasdaq|nyse|tsx|buy shares?|sell shares?)\b",
            message,
            re.I,
        ))
        if (
            candidate in {"TCP", "UDP", "HTTP", "HTTPS", "DNS", "TLS"}
            and network_context
            and not financial_context
        ):
            continue

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


TRAINING_RESULTS_PATTERN = re.compile(
    r"\b("
    r"report|show|give|tell|summari[sz]e|review|what"
    r")\b"
    r".{0,100}"
    r"\b("
    r"training|training session|training run"
    r")\b"
    r".{0,100}"
    r"\b("
    r"result|results|stat|stats|statistics|metrics|"
    r"complete|completed|ran|run"
    r")\b",
    re.IGNORECASE,
)


CANADIAN_MARKET_TODAY_PATTERN = re.compile(
    r"(?:"
        r"\b(?:tsx|toronto stock exchange)\b"
        r".{0,120}"
        r"\b(?:today|current|currently|now|session|doing|look like)\b"
    r"|"
        r"\b(?:canadian|canada)\b"
        r".{0,120}"
        r"\b(?:market|stock market|stocks|index|tsx)\b"
        r".{0,120}"
        r"\b(?:today|current|currently|now|session|doing|look like)\b"
    r")",
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


    training_results_match = (
        TRAINING_RESULTS_PATTERN.search(
            clean
        )
    )

    if training_results_match:
        return ChatIntent(
            intent="training_results",
            family="TRAINING",
            subtype="training_results_followup",
            confidence=1.0,
        )


    canadian_market_today_match = (
        CANADIAN_MARKET_TODAY_PATTERN.search(
            clean
        )
    )

    if canadian_market_today_match:
        return ChatIntent(
            intent="canadian_market_today",
            symbol="^GSPTSE",
            family="MARKET",
            subtype="canadian_market_today",
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


    # NEUROVEST_R116_G40_R23_SCIENCE_FINANCE_DISAMBIGUATION
    # Financial symbols can overlap scientific abbreviations (DNA).
    # This applies only to explicit scientific education questions.
    # Existing safety, developer and privileged-command checks above
    # retain their precedence.
    _g40_r23_educational = bool(re.search(
        r"\b(?:what is|what are|explain|compare|difference"
        r"|how does|how do|define|describe)\b",
        clean, re.I,
    ))
    _g40_r23_scientific = bool(re.search(
        r"\b(?:dna|rna|proteins?|genes?|genetics?"
        r"|nucleotides?|ribosomes?|cells?|biology)\b",
        clean, re.I,
    ))
    _g40_r23_financial = bool(re.search(
        r"\b(?:stock|stocks|ticker|share price|shares"
        r"|trading|broker|buy|sell|short|options?"
        r"|portfolio|market cap|valuation|earnings"
        r"|nasdaq|nyse|tsx|order)\b",
        clean, re.I,
    ))
    if (
        _g40_r23_educational
        and _g40_r23_scientific
        and not _g40_r23_financial
    ):
        return ChatIntent(
            intent="general_conversation",
            family="GENERAL",
            subtype="science_education",
            confidence=1.0,
        )

    # G41_NETWORK_EDUCATION_PRIORITY
    # This remains below existing privileged/safety checks.
    _g41_network_education = bool(re.search(
        r"\b(?:explain|compare|define|describe|difference"
        r"|how does|how do|what is|what are)\b",
        clean, re.I,
    )) and bool(re.search(
        r"\b(?:tcp|udp|http|https|tls|dns)\b",
        clean, re.I,
    )) and not bool(re.search(
        r"\b(?:ticker|stock|shares?|quote|share price"
        r"|market cap|nasdaq|nyse|tsx|buy|sell"
        r"|broker|trade|trading|portfolio)\b",
        clean, re.I,
    ))

    if _g41_network_education:
        return ChatIntent(
            intent="general_conversation",
            family="GENERAL",
            subtype="network_protocol_education",
            confidence=1.0,
        )

    # NEUROVEST_R116_G40_GENERAL_PROGRAMMING_EDUCATION
    # Advisory classification only. Safety, command and developer
    # controls above this point keep their existing precedence.
    _g40_educational = bool(re.search(
        r"\b(explain|define|compare|difference|"
        r"how to|what is|why does)\b",
        clean, re.I,
    ))
    _g40_programming = bool(re.search(
        r"\b(python|javascript|typescript|sql|json|"
        r"rest api|apis|linux service|recursion|asyncio|"
        r"programming)\b",
        clean, re.I,
    ))
    _g40_execution_request = bool(re.search(
        r"\b(place|execute|submit)\b.{0,60}"
        r"\b(real|live|broker|order|trade)\b",
        clean, re.I,
    ))
    # V36-R3R7 — mixed code + strategy remains developer.
    if (
        re.search(
            r"\bSSRN_3247865_[0-9]{3}\b",
            clean,
            flags=re.IGNORECASE,
        )
        and re.search(
            r"\b(python|async|await|code|coding|typescript|javascript|fastapi)\b",
            clean,
            flags=re.IGNORECASE,
        )
        and re.search(
            r"\b(also|separate|distinguish|then|while)\b",
            clean,
            flags=re.IGNORECASE,
        )
    ):
        return ChatIntent(
            intent="general_conversation",
            family="DEVELOPER",
            subtype="mixed_developer_strategy",
            confidence=1.0,
            developer_mode=True,
        )
    if (
        _g40_educational
        and _g40_programming
        and not _g40_execution_request
    ):
        return ChatIntent(
            intent="general_conversation",
            family="GENERAL",
            subtype="software_education",
            confidence=1.0,
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



    # V36-R3R7 compatibility rule:
    #
    # Plain "Explain diversification." remains the established
    # GENERAL/discussion behavior.
    #
    # Only promote to finance reasoning when the question explicitly
    # asks about expected return or risk semantics.
    has_diversification = bool(
        re.search(
            r"\b(diversification|diversified)\b",
            clean,
            flags=re.IGNORECASE,
        )
    )

    has_finance_semantic_relation = bool(
        re.search(
            r"\b(expected returns?|idiosyncratic risk|"
            r"concentration risk)\b",
            clean,
            flags=re.IGNORECASE,
        )
    )

    if (
        has_diversification
        and has_finance_semantic_relation
    ):
        return ChatIntent(
            intent="trading_conversation",
            family="MARKET",
            subtype="general_finance_reasoning",
            confidence=1.0,
        )

    # Explicit strategy creation must remain a trading conversation when
    # "paper trade" appears only inside non-execution safety language.
    #
    # RESEARCH_PATTERNS intentionally recognizes the standalone word
    # "paper" for academic/repository questions. Without this precedence
    # guard, phrases such as "do not paper trade" incorrectly preempt the
    # later strategy/trading classifier.
    explicit_strategy_creation = bool(
        re.search(
            r"\b(create|build|design|draft|develop|propose)\b"
            r".{0,120}\bstrateg(?:y|ies)\b",
            clean,
            flags=re.IGNORECASE,
        )
    )

    nonexecution_paper_trade_language = bool(
        re.search(
            r"\b(do not|don't|never|without)\b"
            r".{0,80}\bpaper\s+trad(?:e|ing)\b",
            clean,
            flags=re.IGNORECASE,
        )
    )

    explicit_research_language = bool(
        re.search(
            r"\b("
            r"ssrn|research\s+papers?|academic\s+papers?|"
            r"journal|journals|citation|citations|"
            r"academic\s+research|research\s+study|research\s+studies|"
            r"corpus|document\s+research"
            r")\b",
            clean,
            flags=re.IGNORECASE,
        )
    )

    explicit_strategy_creation_with_nonexecution_paper_trade = (
        explicit_strategy_creation
        and nonexecution_paper_trade_language
        and not explicit_research_language
    )

    if explicit_strategy_creation_with_nonexecution_paper_trade:
        return ChatIntent(
            intent="trading_conversation",
            symbol=_extract_symbol(
                clean
            ),
            family="MARKET",
            subtype="market_analysis",
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


# NEUROVEST_G43_R42A_ALIGNMENT
import os as _r42a_os

_r42a_previous_detect = detect_chat_intent

def detect_chat_intent(message):
    decision = _r42a_previous_detect(message)
    if _r42a_os.environ.get("NV_R42A_ALIGNMENT_ENABLED") != "1":
        return decision
    from backend.app.stacks.chat_public.routing_alignment_r42a import align_intent
    return align_intent(message, decision)
