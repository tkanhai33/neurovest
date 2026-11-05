from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

NUMBER = r"([0-9][0-9,]*(?:\.[0-9]+)?)"

@dataclass(frozen=True)
class MathResult:
    kind: str
    value: str
    explanation: str

def dec(value: str) -> Decimal:
    return Decimal(value.replace(",", ""))

def money(value: Decimal) -> str:
    return f"{value:,.2f}"

def solve(question: str) -> MathResult | None:
    if not isinstance(question, str) or len(question) > 1200:
        return None

    q = question.strip()

    # Entire expressions, not partial operator matches.
    m = re.fullmatch(
        r"\s*(?:Calculate|Compute|Evaluate)\s+"
        r"\(?\s*" + NUMBER
        + r"\s*\*\s*" + NUMBER
        + r"\s*\)?\s*/\s*" + NUMBER
        + r"\s+exactly\..*",
        q, re.I | re.S,
    )
    if m:
        a, b, c = map(dec, m.groups())
        if c == 0:
            return None
        result = (a * b) / c
        if result != result.to_integral_value():
            return None
        value = str(int(result))
        return MathResult(
            "cancellation", value,
            f"({a} × {b}) ÷ {c} = {value}."
        )

    m = re.fullmatch(
        r"\s*(?:Calculate|Compute)\s+"
        + NUMBER + r"\s*\+\s*" + NUMBER
        + r"\s*-\s*" + NUMBER
        + r"\.\s*Give the exact number.*",
        q, re.I | re.S,
    )
    if m:
        a, b, c = map(dec, m.groups())
        result = a + b - c
        value = str(int(result))
        return MathResult(
            "addition_subtraction", value,
            f"{a} + {b} = {a+b}; subtract {c} = {value}."
        )

    m = re.fullmatch(
        r"\s*A quantity rises from\s+" + NUMBER
        + r"\s+to\s+" + NUMBER
        + r"\.\s*What is its percentage change"
        + r" to 2 decimal places\?",
        q, re.I | re.S,
    )
    if m:
        old, new = map(dec, m.groups())
        if old == 0:
            return None
        change = ((new-old)/old*100).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        value = f"{change:.2f}"
        return MathResult(
            "percentage_change", value,
            f"({new} − {old}) ÷ {old} × 100 = {value}%."
        )

    m = re.fullmatch(
        r"\s*You pay \$" + NUMBER
        + r"\s+for equipment and then \$" + NUMBER
        + r"\s+in repairs\. If its resale value is \$"
        + NUMBER
        + r", what is net profit in dollars\?",
        q, re.I | re.S,
    )
    if m:
        cost, repairs, resale = map(dec, m.groups())
        profit = resale - cost - repairs
        value = str(int(profit))
        return MathResult(
            "resale_profit", value,
            f"Net profit: ${money(profit)}. "
            f"${money(resale)} − ${money(cost)} "
            f"− ${money(repairs)} = ${money(profit)}."
        )

    m = re.fullmatch(
        r"\s*A project has\s+" + NUMBER
        + r"\s+units divided into\s+" + NUMBER
        + r"\s+equal batches\. What is the quotient and remainder\?",
        q, re.I | re.S,
    )
    if m:
        a, b = map(dec, m.groups())
        if b <= 0 or a < 0 or a != int(a) or b != int(b):
            return None
        quotient, remainder = divmod(int(a), int(b))
        value = f"{quotient} remainder {remainder}"
        return MathResult(
            "quotient_remainder", value,
            f"{int(a)} = {int(b)} × {quotient} + "
            f"{remainder}. Quotient: {quotient}; "
            f"remainder: {remainder}."
        )

    m = re.fullmatch(
        r"\s*A paper portfolio buys\s+" + NUMBER
        + r"\s+shares at \$" + NUMBER
        + r"\s+and sells them at \$" + NUMBER
        + r", with \$" + NUMBER
        + r"\s+total transaction fees\. "
        + r"What is the exact net profit\?"
        + r"\s*No trading instructions\.",
        q, re.I | re.S,
    )
    if m:
        shares, buy, sell, fees = map(dec, m.groups())
        if shares <= 0 or min(buy, sell, fees) < 0:
            return None
        profit = shares * (sell-buy) - fees
        value = str(int(profit))
        return MathResult(
            "paper_profit", value,
            f"Net profit = {shares} × "
            f"(${sell} − ${buy}) − ${fees} "
            f"= ${money(profit)}. "
            "This is a hypothetical calculation, not a trade."
        )

    m = re.fullmatch(
        r"\s*A hypothetical portfolio contains \$"
        + NUMBER + r"\s+in an ETF and \$"
        + NUMBER + r"\s+in cash\. "
        + r"What percentage is invested in the ETF"
        + r" to 2 decimal places\?",
        q, re.I | re.S,
    )
    if m:
        etf, cash = map(dec, m.groups())
        total = etf + cash
        if etf < 0 or cash < 0 or total <= 0:
            return None
        percentage = (etf/total*100).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        value = f"{percentage:.2f}"
        return MathResult(
            "portfolio_weight", value,
            f"ETF weight = ${etf:,} ÷ "
            f"${total:,} × 100 = {value}%."
        )


    # G43-R87 VERIFIED TWO-FORMAT PORTFOLIO ARITHMETIC
    # Strictly hypothetical calculation; no execution authority.
    # Combined transaction fees are deducted exactly once.

    m = re.fullmatch(
        r"\s*A hypothetical paper portfolio buys\s+"
        + NUMBER
        + r"\s+shares for \$" + NUMBER
        + r"\s+each and sells for \$" + NUMBER
        + r"\s+each, with \$" + NUMBER
        + r"\s+total fees\.\s+"
        + r"Calculate exact net profit\.\s+"
        + r"Do not execute a trade\.\s*",
        q,
        re.I,
    )

    r87_kind = "paper_profit_verified_r87"

    if not m:
        m = re.fullmatch(
            r"\s*For a simulated position of\s+"
            + NUMBER
            + r"\s+units, entry \$" + NUMBER
            + r", exit \$" + NUMBER
            + r", total fees \$" + NUMBER
            + r", what is the exact realized profit\?"
            + r"\s+This is arithmetic only\.\s*",
            q,
            re.I,
        )
        r87_kind = "simulated_profit_verified_r87"

    if m:
        units, entry, exit_price, fees = map(dec, m.groups())

        if (
            units <= 0
            or units != units.to_integral_value()
            or min(entry, exit_price, fees) < 0
        ):
            return None

        profit = units * (exit_price - entry) - fees

        value = format(profit, "f")
        if profit == profit.to_integral_value():
            value = str(int(profit))

        return MathResult(
            r87_kind,
            value,
            (
                f"Net profit = {units} x "
                f"(${money(exit_price)} - ${money(entry)}) "
                f"- ${money(fees)} = ${money(profit)}. "
                "Total fees are deducted once. "
                "This is a hypothetical calculation; "
                "no trade was executed."
            ),
        )

    return None
