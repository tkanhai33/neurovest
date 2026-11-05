"""
NeuroVest 10P — bounded natural-language normalization.

Only explicit current-message inputs.
No history inference, external I/O, or broker activity.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

VERSION = "neuro-financial-language-10p-v1"

AMOUNT = r"\$?\s*(\d[\d,]*(?:\.\d{1,4})?)"

ACCOUNT_PATTERNS = (
    re.compile(
        r"\b(?:my\s+)?(?:paper\s+)?"
        r"(?:trading\s+)?(?:account|balance|capital)"
        r"\s*(?:is|has|holds|contains|of|at|worth|=|:)?(?:\s+now)?"
        r"\s*" + AMOUNT + r"\b",
        re.I,
    ),
    re.compile(
        r"\b(?:i(?:'ve| have)?\s+got|i\s+have)"
        r"\s*" + AMOUNT
        + r"\s*(?:in|for)\s+(?:my\s+)?"
        r"(?:paper\s+)?(?:trading\s+)?"
        r"(?:account|portfolio)\b",
        re.I,
    ),
    re.compile(
        r"\$?\s*(\d[\d,]*(?:\.\d{1,4})?)"
        r"\s+(?:paper\s+)?(?:trading\s+)?account\b",
        re.I,
    ),
)

GRAND_PATTERN = re.compile(
    r"\b(?:my\s+)?(?:paper\s+)?"
    r"(?:trading\s+)?account\s+"
    r"(?:is|has|holds|contains|of|at|worth)?\s*"
    r"(one|two|three|four|five|six|seven|eight|"
    r"nine|ten)\s+grand\b",
    re.I,
)

GRAND_ALT_PATTERN = re.compile(
    r"\b(?:i(?:'ve| have)?\s+got|i\s+have)\s+"
    r"(one|two|three|four|five|six|seven|eight|"
    r"nine|ten)\s+grand\s+"
    r"(?:in|for)\s+(?:my\s+)?"
    r"(?:paper\s+)?(?:trading\s+)?account\b",
    re.I,
)

WORD_VALUES = {
    "one": 1000, "two": 2000, "three": 3000,
    "four": 4000, "five": 5000, "six": 6000,
    "seven": 7000, "eight": 8000, "nine": 9000,
    "ten": 10000,
}

RISK_PATTERNS = (
    re.compile(
        r"\b(?:risk|risking|risk\s+setting|"
        r"risk\s+percentage)\s*"
        r"(?:is|at|of|=|:)?(?:\s+now)?\s*"
        r"(\d{1,2}(?:\.\d{1,4})?)\s*%",
        re.I,
    ),
    re.compile(
        r"\b(\d{1,2}(?:\.\d{1,4})?)\s*%\s*"
        r"(?:risk|per\s+trade|per\s+position)\b",
        re.I,
    ),
)

ENTRY_PATTERN = re.compile(
    r"\bentry(?:\s+price)?\s*"
    r"(?:is|at|of|=|:)?\s*\$?\s*"
    r"(\d[\d,]*(?:\.\d{1,4})?)\b",
    re.I,
)

STOP_PATTERN = re.compile(
    r"\bstop(?:[\s-]*loss)?\s*"
    r"(?:is|at|of|=|:)?\s*\$?\s*"
    r"(\d[\d,]*(?:\.\d{1,4})?)\b",
    re.I,
)


def _unique(values):
    if not values:
        return None

    try:
        parsed = {
            Decimal(str(value).replace(",", ""))
            for value in values
        }
    except InvalidOperation:
        return None

    if len(parsed) != 1:
        return None

    value = next(iter(parsed))

    if not value.is_finite():
        return None

    return value


def _matches(patterns, message):
    result = []

    for pattern in patterns:
        result.extend(pattern.findall(message))

    return result


def normalize_explicit_risk_message(message: str):
    """
    Return canonical current-message financial inputs,
    or None if insufficient or conflicting.

    Nothing is inferred from conversation history.
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")

    if not message or len(message) > 4000:
        return None

    amounts = _matches(ACCOUNT_PATTERNS, message)

    for pattern in (GRAND_PATTERN, GRAND_ALT_PATTERN):
        for word in pattern.findall(message):
            amounts.append(str(WORD_VALUES[word.lower()]))

    account = _unique(amounts)
    risk = _unique(_matches(RISK_PATTERNS, message))

    if account is None or risk is None:
        return None

    if (
        account <= 0
        or account > Decimal("1000000000000")
        or risk <= 0
        or risk > 100
    ):
        return None

    entry_values = _matches((ENTRY_PATTERN,), message)
    stop_values = _matches((STOP_PATTERN,), message)

    # Conflicting explicit prices invalidate the
    # entire normalization rather than choosing one.
    if len({
        str(Decimal(x.replace(",", "")))
        for x in entry_values
    }) > 1:
        return None

    if len({
        str(Decimal(x.replace(",", "")))
        for x in stop_values
    }) > 1:
        return None

    # NEUROVEST_FINANCIAL_FAIL_CLOSED_10Q
    # A single explicit entry or stop is incomplete.
    # Do not silently drop the supplied price.
    if bool(entry_values) != bool(stop_values):
        return None

    entry = _unique(entry_values)
    stop = _unique(stop_values)

    canonical = (
        f"Account is ${account:f}, "
        f"risk {risk:f}%"
    )

    if entry is not None and stop is not None:
        if (
            entry <= 0
            or stop < 0
            or entry > Decimal("1000000000")
            or stop > Decimal("1000000000")
        ):
            return None

        canonical += (
            f", entry ${entry:f}, stop ${stop:f}"
        )

    return canonical


def trusted_quote_state(
    *,
    symbol: str,
    evidence_origin: str,
    provider_authenticated: bool,
    observed_at: str | None,
):
    """
    Provenance qualification only.

    No price fetching. No claim of quote freshness.
    An arbitrary caller's verified=True flag does
    not establish provider authentication.
    """
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")

    symbol = symbol.strip().upper()

    if not re.fullmatch(r"[A-Z][A-Z0-9.]{0,11}", symbol):
        raise ValueError("invalid symbol")

    # Until real market-data provenance is wired,
    # we deliberately do not trust this standalone
    # adapter to attest to a provider result.
    return {
        "symbol": symbol,
        "state": "provider_provenance_not_established",
        "trusted": False,
        "freshness_verified": False,
        "quote_available": False,
    }
