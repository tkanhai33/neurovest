
"""11H: owner-scoped hypothetical risk calculations.

Uses only identity-verified history records supplied by
the authenticated history loader. Never consults a
broker, portfolio, database, or external service.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

TOPIC_CHANGE = re.compile(
    r"^\s*(?:new topic|switching topics|"
    r"changing the subject|unrelated question)\b",
    re.I,
)

RISK_REQUEST = re.compile(
    r"\b(?:risk|risking)\s+"
    r"(\d{1,3}(?:\.\d{1,3})?)\s*%"
    r"(?:\s+per\s+trade)?\b",
    re.I,
)

RISK_ALTERNATE = re.compile(
    r"\b(\d{1,3}(?:\.\d{1,3})?)\s*%"
    r"\s+(?:risk|per trade)\b",
    re.I,
)

MONEY = re.compile(
    r"(?<![\w])\$\s*"
    r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d{1,2})?)\b"
)

ACCOUNT = re.compile(
    r"\b(?:account|balance|capital)\b",
    re.I,
)

HYPOTHETICAL = re.compile(
    r"\b(?:hypothetical|paper[\s-]?trading|"
    r"paper account|simulation|simulated|example)\b",
    re.I,
)

def field(record, name):
    if isinstance(record, dict):
        return record.get(name)
    return getattr(record, name, None)

def financial_risk_note(
    *,
    owner_user_id,
    thread_id,
    records,
    current_message,
):
    owner = str(owner_user_id or "").strip()
    thread = str(thread_id or "").strip()

    if not owner or not thread:
        return ""

    if not isinstance(current_message, str):
        return ""

    current = current_message.strip()

    if not current or len(current) > 1000:
        return ""

    if TOPIC_CHANGE.search(current):
        return ""

    matched = (
        RISK_REQUEST.search(current)
        or RISK_ALTERNATE.search(current)
    )

    if not matched:
        return ""

    try:
        percentage = Decimal(matched.group(1))
    except InvalidOperation:
        return ""

    if not (Decimal("0") < percentage <= Decimal("100")):
        return ""

    # A new amount in the current turn takes precedence
    # and should be handled by the current-turn analyzer,
    # not silently overridden by earlier history.
    if MONEY.search(current):
        return ""

    if not isinstance(records, (list, tuple)):
        return ""

    historical = []

    for record in records:
        if str(field(record, "user_id") or "") != owner:
            return ""

        if str(field(record, "thread_id") or "") != thread:
            return ""

        role = str(field(record, "role") or "").lower()

        if role != "user":
            continue

        content = field(record, "content")

        if isinstance(content, str) and len(content) <= 2000:
            historical.append(content.strip())

    # Most recent qualifying user value, stopping at
    # an explicit historical topic-change boundary.
    for content in reversed(historical[-12:]):
        if TOPIC_CHANGE.search(content):
            break

        if not ACCOUNT.search(content):
            continue

        if not HYPOTHETICAL.search(content):
            continue

        amounts = MONEY.findall(content)

        # Do not select between multiple competing amounts.
        if len(amounts) != 1:
            return ""

        try:
            balance = Decimal(
                amounts[0].replace(",", "")
            )
        except InvalidOperation:
            return ""

        if not (
            Decimal("0") < balance
            <= Decimal("1000000000000")
        ):
            return ""

        amount = (
            balance * percentage / Decimal("100")
        ).quantize(Decimal("0.01"))

        return (
            "\n\n[NEUROVEST_TRUSTED_FINANCIAL_MATH_11H]\n"
            "Authenticated same-owner, same-thread "
            "conversation calculation. "
            "This is user-supplied hypothetical data, "
            "NOT verified brokerage information.\n"
            f"Hypothetical account: ${balance:,.2f}\n"
            f"Risk percentage: {percentage}%\n"
            f"Calculated risk per trade: ${amount:,.2f}\n"
            "Answer the user's numerical question directly. "
            "Explain the calculation briefly. "
            "Do not claim the balance or trading authority "
            "was verified by a broker.\n"
            "[/NEUROVEST_TRUSTED_FINANCIAL_MATH_11H]\n"
        )

    return ""
