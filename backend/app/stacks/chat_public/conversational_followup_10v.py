"""
NeuroVest 10V — bounded contextual financial follow-ups.

Only use history explicitly marked by the application
as authenticated owner-scoped user conversation.

Never use retrieved articles, model-generated text,
other owners' history, or arbitrary prompt content
as authoritative financial account data.

This module provides user-input calculations only.
It does not verify an account, request quotes, or trade.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

VERSION = "neuro-conversational-followup-10v-v1"

BEGIN = "[NEUROVEST_OWNER_SCOPED_USER_TURNS]"
END = "[/NEUROVEST_OWNER_SCOPED_USER_TURNS]"

MAX_HISTORY_CHARS = 12000
MAX_USER_TURNS = 8

MONEY = r"\$?\s*(\d{1,9}(?:,\d{3})*(?:\.\d{1,2})?)"

ACCOUNT = re.compile(
    r"\b(?:account|balance|capital|portfolio)\s*"
    r"(?:value|size|balance|is|of|=|:)?\s*"
    r"(?:now\s+)?"
    + MONEY,
    re.I,
)

RISK = re.compile(
    r"\b(?:risk|risking)\s*"
    r"(?:is|of|=|:)?\s*"
    r"(\d{1,2}(?:\.\d{1,2})?)\s*%",
    re.I,
)

RISK_CHANGE = re.compile(
    r"\b(?:change|increase|decrease|raise|lower|"
    r"set|make|adjust|switch)\b"
    r".{0,55}\b(?:risk|risking|it|that)\b"
    r".{0,30}\b(?:to|at)\s*"
    r"(\d{1,2}(?:\.\d{1,2})?)\s*%",
    re.I | re.S,
)

RISK_DIRECT = re.compile(
    r"\b(?:what if|how about|instead|actually|"
    r"make that|change that)\b"
    r".{0,65}?\b(?:to|at|risk|risking)\s*"
    r"(\d{1,2}(?:\.\d{1,2})?)\s*%",
    re.I | re.S,
)

SHORT_RISK = re.compile(
    r"^\s*(?:risk\s*)?(\d{1,2}(?:\.\d{1,2})?)\s*%"
    r"(?:\s+instead)?[.!?]?\s*$",
    re.I,
)

ENTRY_OR_STOP = re.compile(
    r"\b(entry|stop|stop-loss|stoploss)\b",
    re.I,
)


@dataclass(frozen=True)
class FollowupResult:
    account_value: Decimal
    risk_percent: Decimal
    risk_budget: Decimal
    previous_turns_considered: int
    owner_data_verified: bool = False
    orders_placed: bool = False


def _number(value: str) -> Decimal | None:
    try:
        amount = Decimal(
            value.replace(",", "").replace("$", "").strip()
        )
    except (InvalidOperation, AttributeError):
        return None

    if not amount.is_finite():
        return None

    return amount


def _extract_history(context: str) -> list[str]:
    if not isinstance(context, str):
        return []

    if context.count(BEGIN) != 1 or context.count(END) != 1:
        return []

    start = context.index(BEGIN) + len(BEGIN)
    finish = context.index(END)

    if start >= finish:
        return []

    content = context[start:finish]

    if len(content) > MAX_HISTORY_CHARS:
        return []

    lines = [
        line[5:].strip()
        for line in content.splitlines()
        if line.startswith("USER:")
    ]

    if not lines or len(lines) > MAX_USER_TURNS:
        return []

    if any(not line or len(line) > 1500 for line in lines):
        return []

    return lines


def resolve_followup_risk(
    context: str,
    current_message: str,
) -> FollowupResult | None:
    """
    Resolve one explicit percentage-change follow-up.

    The historical account value is drawn exclusively
    from a bounded owner-scoped user-turn block.

    Conflicts fail closed. No entry/stop levels are
    carried over or used for position sizing.
    """
    if not isinstance(current_message, str):
        return None

    if len(current_message) > 1500:
        return None

    history = _extract_history(context)

    if not history:
        return None

    # Explicit new calculations with their own account
    # values remain handled by the established 10O/10Q path.
    if ACCOUNT.search(current_message):
        return None

    if ENTRY_OR_STOP.search(current_message):
        return None

    matches = []

    for pattern in (
        RISK_CHANGE,
        RISK_DIRECT,
        SHORT_RISK,
    ):
        matches.extend(pattern.findall(current_message))

    if not matches:
        return None

    # NEUROVEST_10V_R2_CONFLICT_GUARD
    all_percentages = re.findall(
        r"(?<![\w.])(\d{1,3}(?:\.\d{1,2})?)\s*%",
        current_message,
    )

    values = [_number(v) for v in all_percentages]

    if (
        not values
        or any(v is None for v in values)
        or len(set(values)) != 1
    ):
        return None

    normalized = {_number(value) for value in matches}

    if len(normalized) != 1 or next(iter(normalized)) != values[0]:
        return None

    risk_percent = values[0]

    if (
        risk_percent is None
        or risk_percent <= 0
        or risk_percent > 100
    ):
        return None

    # Keep only the last unambiguous historical account
    # statement. Do not silently choose between two
    # different balances stated in the same turn.
    account_value = None

    for turn in reversed(history):
        found = ACCOUNT.findall(turn)

        if not found:
            continue

        amounts = [_number(value) for value in found]

        if (
            any(amount is None for amount in amounts)
            or len(set(amounts)) != 1
        ):
            return None

        account_value = amounts[0]
        break

    if (
        account_value is None
        or account_value <= 0
    ):
        return None

    budget = (
        account_value * risk_percent / Decimal("100")
    ).quantize(Decimal("0.01"))

    return FollowupResult(
        account_value=account_value,
        risk_percent=risk_percent,
        risk_budget=budget,
        previous_turns_considered=len(history),
    )


def append_followup_evidence(
    context: str,
    current_message: str,
) -> str:
    """
    Add conversational evidence only when a complete,
    unambiguous owner-scoped follow-up is available.
    """
    result = resolve_followup_risk(
        context,
        current_message,
    )

    if result is None:
        return context

    # Do not replace existing deterministic calculations.
    if "NEUROVEST_FINANCIAL_REASONING_10O" in context:
        return context

    import json

    evidence = {
        "type": "user_provided_risk_followup",
        "account_value": str(result.account_value),
        "risk_percent": str(result.risk_percent),
        "risk_budget": str(result.risk_budget),
        "account_verified": False,
        "buying_power_checked": False,
        "orders_placed": False,
        "position_size_calculated": False,
        "source": "bounded_owner_scoped_user_turns",
    }

    return (
        context
        + "\n\n[NEUROVEST_CONTEXTUAL_RISK_10V]\n"
        + json.dumps(
            evidence,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n[/NEUROVEST_CONTEXTUAL_RISK_10V]\n"
        + "Explain the user-provided risk budget naturally. "
        + "Do not claim the account balance is verified. "
        + "Do not infer entry, stop, share quantity, "
        + "buying power, or permission to execute orders."
    )
