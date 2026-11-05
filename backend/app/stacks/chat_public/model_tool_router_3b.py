from __future__ import annotations

import asyncio
import json
import os
import re
import urllib.request
from dataclasses import dataclass

# Neuro uses its existing local Ollama installation.
# The planner is a bounded additional inference call;
# it does not load a second model or use a paid API.

TOOL_NONE = "none"
TOOL_SHOW = "universe_show"
TOOL_ANALYZE = "universe_analyze"

ALLOWED_TOOLS = frozenset({
    TOOL_NONE,
    TOOL_SHOW,
    TOOL_ANALYZE,
})

FINANCE_HINT = re.compile(
    r"\b("
    r"market|research|watchlist|universe|"
    r"stock|stocks|ticker|tickers|"
    r"portfolio|etf|etfs|financial|"
    r"analy[sz]e|analysis|compare|"
    r"bullish|bearish|signal|"
    r"buy|sell|hold|trading|"
    r"strategy|strategies"
    r")\b",
    re.IGNORECASE,
)

FOLLOWUP_HINT = re.compile(
    r"\b("
    r"what about|what if|those|these|"
    r"that result|that signal|"
    r"the previous|the last analysis|"
    r"why was|why is|explain that|"
    r"run it again"
    r")\b",
    re.IGNORECASE,
)

UPPER_SYMBOL = re.compile(
    r"\b[A-Z][A-Z0-9]{0,9}\b"
)

STOPWORDS = frozenset({
    "I", "A", "AN", "AND", "OR", "THE",
    "AI", "MY", "ME", "YOU", "YOUR",
    "NEURO", "ETF", "ETFS", "USA",
    "CAN", "DO", "IT", "IS", "TO",
    "FOR", "OF", "ON", "AT", "IN",
    "BUY", "SELL", "HOLD",
    "SHOW", "COMPARE", "ANALYZE",
    "ANALYSIS", "PLEASE", "WHAT",
    "WHY", "HOW", "THIS", "THAT",
})

ROUTE_PREFIX = "NEURO_3B_VERIFIED_ROUTE: "


@dataclass(frozen=True)
class ToolPlan:
    tool: str = TOOL_NONE
    symbols: tuple[str, ...] = ()
    source: str = "none"

    @property
    def command(self) -> str | None:
        if self.tool == TOOL_SHOW:
            return "/universe show"

        if (
            self.tool == TOOL_ANALYZE
            and 2 <= len(self.symbols) <= 12
        ):
            return "/universe analyze " + " ".join(
                self.symbols
            )

        return None


def _symbols(text: str) -> tuple[str, ...]:
    result = []

    for symbol in UPPER_SYMBOL.findall(text):
        if symbol in STOPWORDS:
            continue
        if symbol not in result:
            result.append(symbol)

    return tuple(result[:12])


def _context_symbols(context: str) -> tuple[str, ...]:
    """
    Recover the latest explicitly reported research
    universe from the current conversation context.

    Context must come from the server's authenticated
    conversation assembler, not a browser-supplied
    arbitrary tool-context field.
    """
    if not isinstance(context, str):
        return ()

    matches = re.findall(
        r"(?:Research symbols:|I analyzed)\s*"
        r"([A-Z][A-Z0-9,\s]{1,100})",
        context[-10000:],
    )

    if not matches:
        return ()

    return _symbols(matches[-1])


def _local_model_plan(
    message: str,
    candidates: tuple[str, ...],
    has_context: bool,
) -> dict:
    model = os.getenv(
        "NEURO_3B_PLANNER_MODEL",
        "neuro-reason:latest",
    ).strip()

    if (
        not model
        or len(model) > 120
        or not re.fullmatch(
            r"[A-Za-z0-9._:/-]+", model
        )
    ):
        return {}

    instruction = (
        "You are NeuroVest's tool-selection planner. "
        "Select exactly one tool from: "
        "none, universe_show, universe_analyze. "
        "Return only a JSON object with keys "
        "'tool' and 'symbols'. "
        "Use universe_show only when the user wants "
        "to view their own saved research universe. "
        "Use universe_analyze only when the user "
        "requests a fresh financial analysis or "
        "reanalysis of identified symbols. "
        "Do not call a tool for explanations of previous "
        "results, general questions, writing, coding, "
        "or requests to change account data. "
        "Do not invent symbols or claim tool results. "
        "The supplied candidate symbols are the ONLY "
        "symbols you may choose. "
        "Any proposed tool will undergo server-side "
        "authorization and validation.\n\n"
        f"Prior analysis context available: {has_context}\n"
        f"Allowed symbols: {list(candidates)}\n"
        f"User message: {message[:1200]}\n"
    )

    payload = json.dumps({
        "model": model,
        "prompt": instruction,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 120,
        },
    }).encode("utf-8")

    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=8
        ) as response:
            if response.status != 200:
                return {}

            if response.headers.get(
                "Content-Length"
            ) and int(
                response.headers["Content-Length"]
            ) > 65536:
                return {}

            raw = response.read(65537)

        if len(raw) > 65536:
            return {}

        envelope = json.loads(raw)
        result = json.loads(
            envelope.get("response", "")
        )

        return result if isinstance(
            result, dict
        ) else {}

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ):
        return {}


def _validate_plan(
    raw: dict,
    allowed: tuple[str, ...],
) -> ToolPlan:
    if not isinstance(raw, dict):
        return ToolPlan()

    tool = raw.get("tool")

    if tool not in ALLOWED_TOOLS:
        return ToolPlan()

    if tool == TOOL_SHOW:
        return ToolPlan(
            tool=TOOL_SHOW,
            source="local_model",
        )

    if tool == TOOL_NONE:
        return ToolPlan()

    symbols = raw.get("symbols")

    if not isinstance(symbols, list):
        return ToolPlan()

    if not (
        2 <= len(symbols) <= 12
        and all(
            isinstance(s, str)
            and s in allowed
            for s in symbols
        )
        and len(set(symbols)) == len(symbols)
    ):
        return ToolPlan()

    return ToolPlan(
        tool=TOOL_ANALYZE,
        symbols=tuple(symbols),
        source="local_model",
    )


async def plan_tool(
    *,
    message: str,
    context: str,
) -> ToolPlan:
    """
    Model-directed, read-only tool selection.

    Model output is NEVER an authorization token.
    No developer or admin operations are exposed
    through this initial registry.
    """
    # NEUROVEST_CONVERSATIONAL_QUALITY_3C
    # A question about an existing signal is not a
    # request to recalculate market analysis.

    # NEUROVEST_R65_R2_MODEL_PLANNER_GUARD
    if _nv65_public_research(message):
        return ToolPlan()

    from backend.app.stacks.chat_public.conversation_quality_3c import (
        is_prior_result_explanation,
    )

    if is_prior_result_explanation(message):
        return ToolPlan()

    if not isinstance(message, str):
        return ToolPlan()

    message = message.strip()

    if (
        not message
        or len(message) > 1500
        or message.startswith("/")
    ):
        return ToolPlan()

    if not (
        FINANCE_HINT.search(message)
        or FOLLOWUP_HINT.search(message)
    ):
        return ToolPlan()

    explicit = _symbols(message)
    previous = _context_symbols(context)

    candidates = explicit

    if (
        not candidates
        and FOLLOWUP_HINT.search(message)
    ):
        candidates = previous

    raw = await asyncio.to_thread(
        _local_model_plan,
        message,
        candidates,
        bool(previous),
    )

    plan = _validate_plan(raw, candidates)

    # A model cannot select analysis when no source
    # provides two eligible explicit symbol candidates.
    return plan


def wrap_evidence(
    command: str,
    evidence: str | None,
) -> str | None:
    if not evidence:
        return evidence

    if command not in (
        "/universe show",
    ) and not re.fullmatch(
        r"/universe analyze "
        r"[A-Z0-9]{1,10}"
        r"(?: [A-Z0-9]{1,10}){1,11}",
        command,
    ):
        return evidence

    return (
        ROUTE_PREFIX
        + command
        + "\n"
        + evidence
    )


def unwrap_evidence(
    evidence: str,
):
    if not isinstance(evidence, str):
        return None, evidence

    if not evidence.startswith(ROUTE_PREFIX):
        return None, evidence

    first, sep, remainder = evidence.partition("\n")

    if not sep:
        return None, evidence

    command = first[len(ROUTE_PREFIX):]

    if command == "/universe show":
        return command, remainder

    if re.fullmatch(
        r"/universe analyze "
        r"[A-Z0-9]{1,10}"
        r"(?: [A-Z0-9]{1,10}){1,11}",
        command,
    ):
        return command, remainder

    return None, evidence


# NEUROVEST_13D_R65_R2_PUBLIC_RESEARCH
def _nv65_public_research(message):
    import re

    if not isinstance(message, str):
        return False

    raw = message.strip()

    if not raw or len(raw) > 1500 or raw.startswith("/"):
        return False

    # Owner-specific research and operational requests
    # retain their existing protected routing.
    if re.search(
        r"\b(?:universe|watchlist|portfolio|holdings|"
        r"rebalance|strategy activation|activate strategy|"
        r"place order|execute trade|broker account)\b",
        raw,
        re.I,
    ):
        return False

    if not re.search(
        r"\b(?:compare|comparison|financial|fundamentals?|"
        r"revenue|earnings|gross margin|net income|"
        r"share price|stock price|market quotes?|"
        r"historical|performance|valuation|"
        r"quarterly|annual results|90.day)\b",
        raw,
        re.I,
    ):
        return False

    from backend.app.stacks.chat_public.financial_research_13d_r58 import (
        companies_in_text,
    )

    return bool(companies_in_text(raw))
