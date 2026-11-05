"""
NeuroVest 10O — deterministic financial reasoning.

Pure, bounded calculations using explicitly supplied
current-message inputs.

No database, network, tools, authentication, portfolio
lookup, brokerage execution or account mutations.

Verified arithmetic is NOT verification of account
balances, trades, holdings or market prices.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_DOWN,
    localcontext,
)
from typing import Any, Mapping


VERSION = "neuro-financial-reasoning-10o-v1"

NUMBER = r"(\d{1,12}(?:,\d{3})*(?:\.\d{1,4})?)"

ACCOUNT_RE = re.compile(
    r"\b(?:"
    r"(?:paper[\s-]*trading\s+)?"
    r"(?:account|balance|account\s+value)"
    r"(?:\s+(?:is|of|worth|balance\s+of))?"
    r"\s*[:=]?\s*\$\s*"
    + NUMBER +
    r")\b",
    re.I,
)

RISK_RE = re.compile(
    r"\b(?:risk(?:ing)?|risk\s+percentage|"
    r"risk\s+setting)"
    r"\s*(?:is|of|at|=|:)?\s*"
    r"(\d{1,2}(?:\.\d{1,4})?)\s*%",
    re.I,
)

RISK_ALT_RE = re.compile(
    r"\b(\d{1,2}(?:\.\d{1,4})?)\s*%"
    r"\s*(?:risk|per[\s-]*trade\s+risk)\b",
    re.I,
)

ENTRY_RE = re.compile(
    r"\bentry(?:\s+price)?"
    r"\s*(?:is|at|of|=|:)?\s*\$\s*"
    + NUMBER + r"\b",
    re.I,
)

STOP_RE = re.compile(
    r"\bstop(?:[\s-]*loss)?"
    r"\s*(?:is|at|of|=|:)?\s*\$\s*"
    + NUMBER + r"\b",
    re.I,
)

LIMITED_CONTEXT_MARKER = (
    "[NEUROVEST_DETERMINISTIC_CALCULATION "
    + VERSION + "]"
)


@dataclass(frozen=True)
class RiskEvidence:
    account_value: Decimal
    risk_percent: Decimal
    risk_budget: Decimal
    entry: Decimal | None
    stop: Decimal | None
    risk_per_share: Decimal | None
    max_risk_based_shares: int | None


def _single_decimal(
    pattern: re.Pattern[str],
    message: str,
) -> Decimal | None:
    found = pattern.findall(message)

    if not found:
        return None

    try:
        numbers = {
            Decimal(str(item).replace(",", ""))
            for item in found
        }
    except InvalidOperation:
        return None

    # Conflicting explicit values fail closed.
    if len(numbers) != 1:
        return None

    return next(iter(numbers))


def _risk_fraction(message: str) -> Decimal | None:
    values = []

    for pattern in (RISK_RE, RISK_ALT_RE):
        values.extend(pattern.findall(message))

    if not values:
        return None

    try:
        numbers = {
            Decimal(value)
            for value in values
        }
    except InvalidOperation:
        return None

    if len(numbers) != 1:
        return None

    return next(iter(numbers))


def calculate_explicit_risk(
    message: str,
) -> RiskEvidence | None:
    """
    Calculate only when a current user message
    explicitly specifies its account and risk
    percentage. No history inference.

    Entry and stop must BOTH be supplied to
    calculate risk-based share count.
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")

    if not message or len(message) > 4000:
        return None

    # NEUROVEST_FINANCIAL_LANGUAGE_10P
    # Strict current-message normalization only.
    from backend.app.stacks.chat_public.financial_language_10p import (
        normalize_explicit_risk_message,
    )

    normalized = normalize_explicit_risk_message(message)

    # NEUROVEST_FINANCIAL_FAIL_CLOSED_10Q
    # No fallback to older parsing after normalization rejects.
    if normalized is None:
        return None

    message = normalized

    account = _single_decimal(
        ACCOUNT_RE, message
    )
    risk_percent = _risk_fraction(message)

    if account is None or risk_percent is None:
        return None

    if (
        account <= 0
        or account > Decimal("1000000000000")
        or risk_percent <= 0
        or risk_percent > Decimal("100")
    ):
        return None

    entry = _single_decimal(ENTRY_RE, message)
    stop = _single_decimal(STOP_RE, message)

    if (entry is None) != (stop is None):
        # Budget can be calculated without both prices,
        # but partial stop evidence is omitted.
        entry = None
        stop = None

    with localcontext() as ctx:
        ctx.prec = 40

        budget = (
            account * risk_percent / Decimal("100")
        )

        per_share = None
        shares = None

        if entry is not None and stop is not None:
            if (
                entry <= 0
                or stop < 0
                or entry > Decimal("1000000000")
                or stop > Decimal("1000000000")
            ):
                entry = None
                stop = None
            else:
                per_share = abs(entry - stop)

                if per_share > 0:
                    count = (
                        budget / per_share
                    ).to_integral_value(
                        rounding=ROUND_DOWN
                    )

                    if count <= Decimal("1000000000000"):
                        shares = int(count)

    return RiskEvidence(
        account_value=account,
        risk_percent=risk_percent,
        risk_budget=budget,
        entry=entry,
        stop=stop,
        risk_per_share=per_share,
        max_risk_based_shares=shares,
    )


def _num(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")


def evidence_payload(
    evidence: RiskEvidence,
) -> dict[str, Any]:
    return {
        "evidence_type": "deterministic_risk_calculation",
        "version": VERSION,
        "input_provenance": "current_user_message",
        "inputs_are_account_verified": False,
        "arithmetic_verified": True,
        "account_value": _num(evidence.account_value),
        "risk_percent": _num(evidence.risk_percent),
        "risk_budget": _num(evidence.risk_budget),
        "entry": _num(evidence.entry),
        "stop": _num(evidence.stop),
        "risk_per_share": _num(evidence.risk_per_share),
        "max_risk_based_shares": (
            evidence.max_risk_based_shares
        ),
        "buying_power_checked": False,
        "fees_checked": False,
        "slippage_checked": False,
        "orders_placed": False,
    }


def _nv10v_original_augment_model_context(
    context: str,
    message: str,
) -> str:
    if not isinstance(context, str):
        raise TypeError("context must be a string")

    if not isinstance(message, str):
        raise TypeError("message must be a string")

    if LIMITED_CONTEXT_MARKER in context:
        return context

    if not context.strip():
        return context

    evidence = calculate_explicit_risk(message)

    if evidence is None:
        return context

    payload = evidence_payload(evidence)

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return (
        context.rstrip()
        + "\n\n"
        + LIMITED_CONTEXT_MARKER
        + "\n"
        + serialized
        + "\n"
        + "[/NEUROVEST_DETERMINISTIC_CALCULATION]"
        + "\n\n"
        + "Arithmetic above was independently calculated "
        + "from unverified current-user inputs. "
        + "Use it for the requested hypothetical "
        + "calculation only. Never describe the balance "
        + "as broker-verified or an order as executed."
    )

# NEUROVEST_CONVERSATIONAL_FOLLOWUP_10V
from functools import wraps as _nv10v_wraps

@_nv10v_wraps(_nv10v_original_augment_model_context)
def augment_model_context(context: str, message: str) -> str:
    from backend.app.stacks.chat_public.conversational_followup_10v import (
        append_followup_evidence,
    )

    existing = _nv10v_original_augment_model_context(
        context,
        message,
    )

    return append_followup_evidence(
        existing,
        message,
    )




def format_market_evidence(
    *,
    symbol: str,
    price: str | None,
    source: str | None,
    observed_at: str | None,
    verified: bool,
) -> dict[str, Any]:
    """
    Pure structured market-evidence adapter.

    This does not fetch quotes. Only the caller may
    supply a trusted provider result. Unverified data
    is never represented as a verified live price.
    """
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")

    symbol = symbol.strip().upper()

    if not re.fullmatch(r"[A-Z][A-Z0-9.]{0,11}", symbol):
        raise ValueError("invalid symbol")

    valid = (
        verified is True
        and isinstance(price, str)
        and isinstance(source, str)
        and isinstance(observed_at, str)
        and bool(source.strip())
        and bool(observed_at.strip())
    )

    parsed = None

    if valid:
        try:
            parsed = Decimal(price)
            valid = parsed.is_finite() and parsed > 0
        except (InvalidOperation, ValueError):
            valid = False

    if not valid:
        return {
            "symbol": symbol,
            "state": "not_verified",
            "verified_quote": None,
            "source": None,
            "observed_at": None,
        }

    return {
        "symbol": symbol,
        "state": "provided_as_verified",
        "verified_quote": _num(parsed),
        "source": source.strip(),
        "observed_at": observed_at.strip(),
    }
