from __future__ import annotations

import json
import re
from typing import Any


ANALYSIS_INTENT = re.compile(
    r"\b("
    r"analy[sz]e|"
    r"analysis of|"
    r"evaluate|"
    r"run (?:an? )?analysis (?:on|of|for)"
    r")\b",
    re.IGNORECASE,
)

SHOW_INTENT = re.compile(
    r"\b("
    r"show|list|display|view|"
    r"what(?:'s| is)|which"
    r")\b",
    re.IGNORECASE,
)

UNIVERSE_TOPIC = re.compile(
    r"\b("
    r"my research universe|"
    r"my universe|"
    r"my watchlist|"
    r"my research symbols|"
    r"my saved symbols"
    r")\b",
    re.IGNORECASE,
)

STOPWORDS = frozenset({
    "A", "AN", "AND", "OR", "THE",
    "MY", "ME", "I", "YOU", "YOUR",
    "PLEASE", "CAN", "COULD", "WOULD",
    "NEURO", "FOR", "OF", "ON", "WITH",
    "TO", "IN", "IS", "IT", "THESE",
    "THOSE", "TELL", "ABOUT",
    "ETF", "ETFS", "STOCK", "STOCKS",
    "SYMBOL", "SYMBOLS", "TICKER",
    "TICKERS", "THANKS", "NOW",
    "TODAY", "MARKET", "DO",
    "WHAT", "HOW", "LOOK",
    "ARE", "THEY", "AT", "THEN",
    "RUN", "ANALYSIS", "ANALYZE",
    "ANALYSE", "EVALUATE",
    "COMPLETE", "CURRENT", "LATEST",
    "RESEARCH", "UNIVERSE",
    "WATCHLIST", "PORTFOLIO",
    "BULLISH", "BEARISH",
    "TRADING", "PRICE",
})


def natural_command(message: str) -> str | None:
    """
    Convert supported, explicit natural-language
    research requests into existing trusted operations.

    This function never executes an operation itself.

    Unrecognized conversation remains with the
    general-purpose language model.
    """

    # NEUROVEST_R65_R2_NATURAL_GUARD
    if _nv65_public_research(message):
        return None

    if not isinstance(message, str):
        return None

    raw = message.strip()

    if not raw or len(raw) > 1500:
        return None

    if raw.startswith("/"):
        return None

    if (
        SHOW_INTENT.search(raw)
        and UNIVERSE_TOPIC.search(raw)
        and not ANALYSIS_INTENT.search(raw)
    ):
        return "/universe show"

    intent = ANALYSIS_INTENT.search(raw)

    if intent is None:
        return None

    remainder = raw[intent.end():]

    # Explicit uppercase ticker symbols only.
    # No invented symbols and no guessing from prose.
    tokens = re.findall(
        r"\b[A-Z][A-Z0-9]{0,9}\b",
        remainder,
    )

    selected = []

    for token in tokens:
        if token in STOPWORDS:
            continue

        selected.append(token)

    # Requests without a clear symbol list remain
    # in ordinary conversation.
    #
    # The underlying owner-scoped validator still
    # checks membership, uniqueness and eligibility.
    if not 2 <= len(selected) <= 12:
        return None

    return (
        "/universe analyze "
        + " ".join(selected)
    )


def _extract_analysis(
    evidence: str,
) -> dict[str, Any] | None:
    if not isinstance(evidence, str):
        return None

    prefix = (
        "UNIVERSE_COMMAND_STATUS: ANALYZED"
    )

    if not evidence.startswith(prefix):
        return None

    marker = "Verified engine evidence:"

    if marker not in evidence:
        return None

    raw = evidence.split(marker, 1)[1].lstrip()

    try:
        value, _ = json.JSONDecoder().raw_decode(raw)
    except (ValueError, TypeError):
        return None

    if not isinstance(value, dict):
        return None

    return value


def explain_verified_analysis(
    evidence: str,
    fallback: str,
) -> str:
    """
    Transform existing verified engine data into
    a natural explanation.

    Never invent missing data or unsupported
    conclusions.

    Fall back to the existing authoritative
    response when evidence cannot be parsed.
    """
    details = _extract_analysis(evidence)

    if details is None:
        return fallback

    aggregate = details.get(
        "strategy_aggregation"
    )

    if not isinstance(aggregate, dict):
        return fallback

    match = re.search(
        r"Research symbols:\s*([^\n]+)",
        evidence,
    )

    if match is None:
        return fallback

    symbols = match.group(1).strip()

    buy = aggregate.get("buy_votes")
    sell = aggregate.get("sell_votes")
    hold = aggregate.get("hold_votes")
    count = aggregate.get("received_results")
    confidence = aggregate.get("confidence")
    decision = aggregate.get("decision")

    if not (
        all(
            type(value) is int and value >= 0
            for value in (buy, sell, hold, count)
        )
        and type(confidence) in (int, float)
        and 0 <= confidence <= 1
        and decision in ("BUY", "SELL", "HOLD")
        and buy + sell + hold <= count
    ):
        return fallback

    lines = [
        "I analyzed " + symbols
        + " using NeuroVest's read-only "
        + "financial research engine.",
        "",
        "Here's what I found:",
        (
            f"{buy} BUY, {sell} SELL, "
            f"and {hold} HOLD results "
            f"across {count} evaluators."
        ),
    ]

    directional = buy + sell

    if directional <= 1 or confidence < 0.05:
        lines.append(
            "The directional evidence is very weak. "
            "I would not interpret this as a strong "
            "buy or sell signal."
        )

    elif hold > count / 2:
        lines.append(
            "Most evaluators are holding rather "
            "than confirming a directional move."
        )

    lines.append(
        "The aggregate engine label is "
        + decision
        + ", with reported confidence of "
        + f"{confidence * 100:.3f}%."
    )

    freshness = details.get("freshness")

    if isinstance(freshness, dict):
        observations = freshness.get("symbols")

        if isinstance(observations, dict):
            dates = sorted({
                str(
                    item.get(
                        "latest_observation_utc"
                    )
                )
                for item in observations.values()
                if isinstance(item, dict)
                and item.get(
                    "latest_observation_utc"
                )
            })

            if dates:
                lines.append(
                    "Latest reported daily "
                    "observations: "
                    + ", ".join(dates[:4])
                    + "."
                )

        if freshness.get(
            "source_freshness_independently_verified"
        ) is False:
            lines.append(
                "Independent source freshness "
                "has not been verified."
            )

        if freshness.get(
            "live_quote_freshness_verified"
        ) is False:
            lines.append(
                "Live-quote freshness has not "
                "been verified."
            )

    lines.extend([
        "",
        "These results are research signals, "
        "not verified brokerage positions.",
        "No trading orders were placed.",
    ])

    return "\n".join(lines)


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
