"""
NeuroVest R107.

Resolve explicitly named companies to ticker symbols,
support bounded financial follow-ups when prior chat context
has one unambiguous company, and add calculated profit
margins from R105's provider-backed annual financial figures.

All names are research aliases, not verified issuer identity.
R105/yfinance must still verify the resolved ticker.

No database, brokerage, trading or authorization access.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

from backend.app.stacks.chat_public.yfinance_issuer_13n_r104c import (
    explicit_ticker,
)

# NEUROVEST_R107_CONTEXTUAL_FINANCIAL_ENGINE

ALIASES = {
    "NVIDIA": "NVDA",
    "NVIDIA CORPORATION": "NVDA",
    "MICROSOFT": "MSFT",
    "MICROSOFT CORPORATION": "MSFT",
    "APPLE": "AAPL",
    "APPLE INC": "AAPL",
    "ADVANCED MICRO DEVICES": "AMD",
    "AMD": "AMD",
    "ALPHABET": "GOOGL",
    "GOOGLE": "GOOGL",
    "META PLATFORMS": "META",
    "META": "META",
    "AMAZON": "AMZN",
    "AMAZON COM": "AMZN",
    "TESLA": "TSLA",
    "INTEL": "INTC",
    "NETFLIX": "NFLX",
}

FINANCIAL = re.compile(
    r"\b("
    r"revenue|earnings|net income|operating income|"
    r"gross profit|profit|profits|profitability|"
    r"margin|margins|financial|financials|"
    r"income statement|sales|fundamentals|"
    r"annual results|year.over.year|growth"
    r")\b",
    re.I,
)

FOLLOWUP = re.compile(
    r"\b("
    r"its|their|that company|this company|"
    r"what about|and the|how about|"
    r"compared to last year|previous year"
    r")\b",
    re.I,
)

EXPLICIT_PRIOR = re.compile(
    r"\b(?:ticker|symbol)\s*(?::|=|is)?\s*"
    r"([A-Z]{2,5})\b",
    re.I,
)

MARGIN_REQUEST = re.compile(
    r"\b("
    r"margins?|profitability|profit margin|"
    r"net margin|operating margin|gross margin"
    r")\b",
    re.I,
)

ROW = re.compile(
    r"^-\s*(Revenue|Net income|Operating income|"
    r"Gross profit);\s*"
    r"(?:fiscal period end|provider statement date)\s*"
    r"(\d{4}-\d{2}-\d{2});\s*"
    r"([A-Z]{3})\s+([0-9,]+)\s*$",
    re.I | re.M,
)

MAX_QUESTION = 3000
MAX_CONTEXT_LOOKBACK = 9000
MAX_RESULT = 7000


def _named_symbols(question):
    matches = set()

    # Longest aliases first to avoid substring confusion.
    for name, ticker in sorted(
        ALIASES.items(),
        key=lambda item: -len(item[0]),
    ):
        if re.search(
            r"(?<!\w)" + re.escape(name) + r"(?!\w)",
            question,
            re.I,
        ):
            matches.add(ticker)

    return matches


def resolve_subject(question, prior_context=""):
    """Resolve one issuer conservatively; never use holdings."""

    if not isinstance(question, str):
        return None

    question = question.strip()

    if not question or len(question) > MAX_QUESTION:
        return None

    # R104 blocks brokerage and other privileged requests.
    # Applying it first keeps the same eligibility boundary.
    from backend.app.stacks.chat_public.yfinance_issuer_13n_r104c import (
        PRIVILEGED,
    )

    if PRIVILEGED.search(question):
        return None

    if not FINANCIAL.search(question):
        return None

    names = _named_symbols(question)
    explicit = explicit_ticker(question)

    if explicit:
        names.add(explicit)

    # Multiple issuers are not silently collapsed.
    if len(names) > 1:
        return None

    if len(names) == 1:
        return next(iter(names))

    # Do not borrow the identity of a previous issuer unless
    # this is recognizably a financial follow-up.
    if not FOLLOWUP.search(question):
        return None

    if not isinstance(prior_context, str):
        return None

    recent = prior_context[-MAX_CONTEXT_LOOKBACK:]

    # Only use an explicit ticker from a user/human message
    # in the existing conversation text. Avoid deriving
    # subjects from general instructions, holdings or tools.
    turns = re.findall(
        r"(?im)^\s*(?:user|human)\s*:\s*"
        r"([^\n]{1,600})",
        recent,
    )

    if not turns:
        return None

    symbols = []

    for turn in turns[-4:]:
        candidates = set(
            x.upper()
            for x in EXPLICIT_PRIOR.findall(turn)
        )

        candidates.update(_named_symbols(turn))

        if len(candidates) == 1:
            symbols.append(next(iter(candidates)))
        elif len(candidates) > 1:
            symbols.append(None)

    # Follow the most recent explicit single-company turn.
    if not symbols or symbols[-1] is None:
        return None

    return symbols[-1]


def _read_rows(evidence):
    values = {}

    for metric, period, currency, amount in ROW.findall(evidence):
        try:
            number = Decimal(amount.replace(",", ""))
        except (InvalidOperation, ValueError):
            continue

        if not number.is_finite() or number < 0:
            continue

        values[(metric.casefold(), period, currency)] = number

    return values


def profit_margin_context(evidence):
    """Compute margins only from matching observed periods."""

    if not isinstance(evidence, str) or not evidence:
        return ""

    values = _read_rows(evidence)

    revenue = {
        (period, currency): amount
        for (metric, period, currency), amount in values.items()
        if metric == "revenue" and amount > 0
    }

    if not revenue:
        return ""

    metric_labels = {
        "net income": "Net profit margin",
        "operating income": "Operating margin",
        "gross profit": "Gross margin",
    }

    lines = []

    for (period, currency), sales in sorted(
        revenue.items(),
        reverse=True,
    )[:2]:
        for metric, label in metric_labels.items():
            income = values.get((metric, period, currency))

            if income is None:
                continue

            ratio = (income / sales) * Decimal(100)

            # Avoid surfacing implausible data as a confident
            # ratio; legitimate negative margins are handled
            # by future signed-statement support.
            if not (Decimal(0) <= ratio <= Decimal(100)):
                continue

            lines.append(
                f"- {label}; provider date {period}; "
                f"{ratio:.2f}%; calculated as "
                f"{metric} / revenue using {currency} figures"
            )

    if not lines:
        return ""

    return "\n".join([
        "[R107 DERIVED FINANCIAL RATIOS]",
        "These are calculated from the R105 provider figures,",
        "not independently sourced filing ratios.",
        *lines,
        "[END R107 DERIVED RATIOS]",
    ])


def build_context(question, model_input, r105_fetch):
    """
    Return financial evidence using R105 as the only
    financial-data provider.

    No provider calls occur for nonfinancial questions
    or questions without one identifiable issuer.
    """

    if not callable(r105_fetch):
        return ""

    ticker = resolve_subject(
        question,
        model_input,
    )

    if ticker is None:
        return ""

    # R105 requires an explicit ticker and financial intent.
    # Feed its original, validated interface rather than
    # inventing a second provider implementation.
    resolved_question = (
        f"Analyze ticker {ticker} revenue and net income, "
        "operating income and gross profit from annual "
        "financial statements."
    )

    try:
        evidence = r105_fetch(resolved_question)
    except Exception:
        return ""

    if not isinstance(evidence, str) or not evidence:
        return ""

    # Never trust a result associated with another symbol.
    if f"Resolved equity symbol: {ticker}\n" not in evidence:
        return ""

    ratios = (
        profit_margin_context(evidence)
        if MARGIN_REQUEST.search(question)
        else ""
    )

    guidance = "\n".join([
        "[R107 RESEARCH RESPONSE GUIDANCE]",
        f"Current researched issuer: {ticker}",
        "Use the financial observations above where relevant.",
        "Answer the current user question directly.",
        "For follow-ups, do not unnecessarily repeat the",
        "entire original financial statement table.",
        "Explain relevant financial trends and their limits.",
        "Do not invent sources, filings, dates or metrics.",
        "Yahoo Finance statement dates are provider labels.",
        "Do not claim they are verified official fiscal year ends.",
        "Do not expose internal R105/R107 evidence markers.",
        "No trade execution, brokerage actions or recommendations",
        "are authorized by this context.",
        "[END R107 GUIDANCE]",
    ])

    # NEUROVEST_R108_PREGEN_DETERMINISTIC_COMPARISON
    # Use matching provider periods for all derived metrics.
    from backend.app.stacks.chat_public.financial_comparison_13r_r108 import (
        build_comparison_context as _nv108_compare,
    )

    comparison = _nv108_compare(evidence)

    result = evidence + "\n\n"

    if comparison:
        result += comparison + "\n\n"

    if ratios:
        result += ratios + "\n\n"

    result += guidance

    return result if len(result) <= MAX_RESULT else ""
