"""
NeuroVest R104-C

Resolve one explicitly requested financial research ticker
using the existing installed yfinance package.

No trading, brokerage operations, database writes, or
authentication changes.

An unresolved, invalid, or ambiguous subject returns None.
"""

from __future__ import annotations

import re

# NEUROVEST_R104C_YFINANCE_ISSUER_RESOLUTION

MAX_QUESTION = 3000

FINANCE = re.compile(
    r"\b("
    r"stock|stocks|ticker|equity|equities|"
    r"shares|revenue|earnings|financial|"
    r"valuation|dividend|income statement|"
    r"balance sheet|cash flow|company"
    r")\b",
    re.I,
)

EXPLICIT = (
    re.compile(
        r"(?<![\w$])\$([A-Z]{1,5})(?![A-Za-z0-9])"
    ),
    re.compile(
        r"\b(?:ticker|symbol)\s*"
        r"(?::|=|is)?\s*([A-Z]{1,5})\b",
        re.I,
    ),
    re.compile(
        r"\b([A-Z]{2,5})\s+"
        r"(?:stock|shares|ticker|revenue|earnings)\b"
    ),
    re.compile(
        r"\(([A-Z]{2,5})\)"
    ),
)

STOPWORDS = {
    "USD", "CAD", "FY", "CEO", "ETF", "SEC",
    "API", "THE", "AND", "FOR", "WITH", "FROM",
    "HTTP", "JSON", "NYSE", "NASDAQ",
}

PRIVILEGED = re.compile(
    r"\b("
    r"execute|place order|buy shares|sell shares|"
    r"submit trade|brokerage|broker order|"
    r"emergency.stop|developer command|"
    r"developer authorization|account permissions|"
    r"withdraw funds|live trading"
    r")\b",
    re.I,
)


def explicit_ticker(question):
    """
    Extract exactly one explicit ticker.

    Do not guess company names, infer a ticker from holdings,
    or choose the first ticker in a multi-company request.
    """

    if not isinstance(question, str):
        return None

    question = question.strip()

    if (
        not question
        or len(question) > MAX_QUESTION
        or not FINANCE.search(question)
        or PRIVILEGED.search(question)
    ):
        return None

    matches = set()

    for pattern in EXPLICIT:
        for match in pattern.finditer(question):
            token = match.group(1).upper()

            if token not in STOPWORDS:
                matches.add(token)

    return next(iter(matches)) if len(matches) == 1 else None


def resolve_with_provider(ticker, provider):
    """
    provider(symbol) returns a yfinance-like Ticker object.

    Only provider-supplied symbol identity is accepted.
    Do not trust longName alone as ticker verification.
    """

    if (
        not isinstance(ticker, str)
        or not re.fullmatch(r"[A-Z]{1,5}", ticker)
        or ticker in STOPWORDS
    ):
        return None

    try:
        instrument = provider(ticker)

        info = instrument.info

        if not isinstance(info, dict):
            return None

        resolved = info.get("symbol")
        quote_type = str(
            info.get("quoteType") or ""
        ).upper()

        if not isinstance(resolved, str):
            return None

        if resolved.strip().upper() != ticker:
            return None

        # R103 currently concerns company financial statements.
        # Do not classify funds, indices, currencies or ETFs
        # as company issuers.
        if quote_type != "EQUITY":
            return None

        return {
            "ticker": ticker,
        }

    except Exception:
        return None


def resolve_research_issuer(question):
    """
    Synchronous provider operation.

    The async runtime integration calls this in a worker
    with a bounded wait to avoid blocking its event loop.
    """

    ticker = explicit_ticker(question)

    if ticker is None:
        return None

    try:
        import yfinance as yf
    except ImportError:
        return None

    return resolve_with_provider(
        ticker,
        yf.Ticker,
    )
